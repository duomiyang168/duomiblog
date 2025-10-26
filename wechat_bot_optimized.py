# wechat_bot_optimized.py
# 微信 4.0.5 + wxauto4 开源版 - 优化版
# 功能：引用回复、并发队列、去重、性能优化

import os
import time
import re
import threading
import queue
from http import HTTPStatus
from typing import Set, Tuple, Optional, Dict, Any, List
from collections import deque
from dataclasses import dataclass
import logging

from dotenv import load_dotenv
from dashscope import Application

from wxauto4 import WeChat
from wxauto4.msgs import Message, FriendMessage

try:
    from wxauto4.param import WxParam
    WxParam.LISTEN_INTERVAL = 1
    WxParam.MESSAGE_HASH = True
    WxParam.FORCE_MESSAGE_XBIAS = True
except Exception:
    pass

load_dotenv()

# ===== 日志配置 =====
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# ===== 配置 =====
TARGET_GROUP_NAME = "多米临时结算"
TRIGGER_PREFIX = "#举手"
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")
APP_ID = "0365f84c253a45698bbfe362eb52c5ba"
REPLY_TEMPLATE = "\n{answer}"

# 并发与超时/限速
WORKERS = 3
TASK_TIMEOUT_SEC = 30
CALL_THROTTLE_MS = 150
SEND_RETRIES = 3
SEND_RETRY_DELAY = 0.3

# 去重与匹配
processed_messages: Set[Tuple[str, str, str]] = set()
processed_questions: Set[str] = set()
MAX_QUESTIONS_CACHE_SIZE = 500
MAX_MESSAGE_CACHE_SIZE = 100

RAISE_HAND_PATTERN = re.compile(r"(#|＃)\s*举手[：:\s]*(.+)", re.IGNORECASE)
NICK_COLON_PREFIX = re.compile(r"^[^:：]+[：:]\s*(.*)$")
INVISIBLE_CHARS = re.compile(r"[\u200b\u200c\u200d\u2060\u00A0]")

# 队列与性能监控
task_queue: "queue.Queue[Dict[str, Any]]" = queue.Queue(maxsize=1000)
stop_event = threading.Event()
last_call_ts = 0.0
queue_stats = {"total": 0, "success": 0, "failed": 0, "timeout": 0}
stats_lock = threading.Lock()

# 消息缓存（用于快速引用回复）
message_cache: deque = deque(maxlen=MAX_MESSAGE_CACHE_SIZE)
cache_lock = threading.Lock()

wx = WeChat()


@dataclass
class CachedMessage:
    """缓存的消息对象"""
    msg: Message
    timestamp: float
    sender: str
    content: str
    normalized_content: str


def now_ms() -> float:
    return time.time() * 1000.0


def throttle_calls(ms: int):
    """API 调用限流"""
    global last_call_ts
    t = now_ms()
    gap = t - last_call_ts
    if gap < ms:
        time.sleep((ms - gap) / 1000.0)
    last_call_ts = now_ms()


def normalize_spaces(s: str) -> str:
    """标准化空白字符"""
    s = INVISIBLE_CHARS.sub("", s or "")
    s = s.replace("：", ":")
    s = s.strip()
    s = re.sub(r"\s+", " ", s)
    return s


def strip_nick_prefix(text: str) -> str:
    """去除昵称前缀"""
    text = normalize_spaces(text)
    m = NICK_COLON_PREFIX.match(text)
    return normalize_spaces(m.group(1)) if m else text


def normalize_question(q: str) -> str:
    """标准化问题文本"""
    return normalize_spaces(q)


def remember_question_once(q: str) -> bool:
    """去重：确保同一问题只处理一次"""
    norm = normalize_question(q)
    key = f"{TARGET_GROUP_NAME}::{norm}"
    if key in processed_questions:
        return False
    if len(processed_questions) > MAX_QUESTIONS_CACHE_SIZE:
        processed_questions.clear()
    processed_questions.add(key)
    return True


def get_chat_name(chat) -> str:
    """获取聊天窗口名称"""
    name = ""
    try:
        name = getattr(chat, "who", "") or ""
        if not name and hasattr(chat, "ChatInfo"):
            info = chat.ChatInfo() or {}
            name = info.get("chat_name", "") or name
    except Exception:
        pass
    return str(name).strip()


def is_group_chat(chat) -> bool:
    """判断是否为群聊"""
    try:
        ctype = getattr(chat, "chat_type", None)
        if isinstance(ctype, str):
            return ctype == "group"
        if hasattr(chat, "ChatInfo"):
            info = chat.ChatInfo() or {}
            return info.get("chat_type", "") == "group"
    except Exception:
        pass
    return True


def is_target_group(chat) -> bool:
    """判断是否为目标群聊"""
    return get_chat_name(chat) == TARGET_GROUP_NAME


def get_all_texts(msg: Message) -> List[str]:
    """获取消息的所有文本内容"""
    try:
        if hasattr(msg, "get_all_text") and callable(msg.get_all_text):
            lst = msg.get_all_text() or []
            return [normalize_spaces(t) for t in lst if str(t).strip()]
    except Exception:
        pass
    primary = str(getattr(msg, "content", "") or getattr(msg, "text", "") or "")
    return [normalize_spaces(primary)] if primary.strip() else []


def extract_question_from_text(text: str) -> Optional[str]:
    """从文本中提取问题"""
    if not text:
        return None
    content = strip_nick_prefix(text)
    m = RAISE_HAND_PATTERN.search(content)
    if not m:
        return None
    question = normalize_spaces(m.group(2))
    return question or None


def extract_question_from_msg(msg: Message) -> Optional[str]:
    """从消息对象中提取问题"""
    segments = get_all_texts(msg)
    for seg in segments:
        q = extract_question_from_text(seg)
        if q:
            return q
    if segments:
        merged = normalize_spaces(" ".join(segments))
        m2 = RAISE_HAND_PATTERN.search(strip_nick_prefix(merged))
        if m2:
            q2 = normalize_spaces(m2.group(2))
            if q2:
                return q2
    return None


def make_message_signature(msg: Message) -> Tuple[str, str, str]:
    """生成消息唯一签名"""
    ts = str(getattr(msg, "timestamp", None) or getattr(msg, "time", None) or time.time())
    sender = str(getattr(msg, "sender", "") or getattr(msg, "author", ""))
    text_segments = get_all_texts(msg)
    all_text = " | ".join(text_segments)
    return (ts, sender, all_text)


def cache_message(msg: Message):
    """缓存消息对象，用于后续引用回复"""
    try:
        sender = str(getattr(msg, "sender", "") or getattr(msg, "author", ""))
        segments = get_all_texts(msg)
        content = " ".join(segments)
        normalized = normalize_spaces(strip_nick_prefix(content))

        cached = CachedMessage(
            msg=msg,
            timestamp=time.time(),
            sender=sender,
            content=content,
            normalized_content=normalized
        )

        with cache_lock:
            message_cache.append(cached)

    except Exception as e:
        logger.debug(f"缓存消息失败: {e}")


def find_cached_message(normalized_content: str, sender: str = "") -> Optional[Message]:
    """从缓存中查找匹配的消息对象"""
    with cache_lock:
        # 从最新的消息开始查找
        for cached in reversed(message_cache):
            if cached.normalized_content == normalized_content:
                if sender and cached.sender and (cached.sender != sender):
                    continue
                return cached.msg
    return None


def parse_dashscope_output(response) -> str:
    """解析 DashScope 响应"""
    out = getattr(response, "output", None)
    if out is None:
        return ""
    text = getattr(out, "text", None)
    if isinstance(text, str) and text.strip():
        return text.strip()
    choices = getattr(out, "choices", None)
    if isinstance(choices, list) and choices:
        first = choices[0]
        msgobj = getattr(first, "message", None)
        if msgobj is not None:
            mcontent = getattr(msgobj, "content", None)
            if isinstance(mcontent, str) and mcontent.strip():
                return mcontent.strip()
        ftext = getattr(first, "text", None)
        if isinstance(ftext, str) and ftext.strip():
            return ftext.strip()
    return str(out).strip()


def call_dashscope(question: str) -> str:
    """调用 DashScope API"""
    if not DASHSCOPE_API_KEY:
        return "系统未配置 DASHSCOPE_API_KEY，无法调用智能答复。"
    throttle_calls(CALL_THROTTLE_MS)
    try:
        response = Application.call(
            api_key=DASHSCOPE_API_KEY,
            app_id=APP_ID,
            prompt=question
        )
    except Exception as e:
        logger.error(f"调用智能服务异常：{e}")
        return f"调用智能服务异常：{e}"
    if response.status_code != HTTPStatus.OK:
        return f"智能服务错误（code={response.status_code}）：{getattr(response, 'message', '')}"
    answer = parse_dashscope_output(response)
    return answer if answer else "暂未获取到有效答案，请稍后再试。"


def try_quote_on_message_obj(msg: Message, reply_text: str) -> bool:
    """尝试直接在消息对象上引用回复"""
    try:
        if hasattr(msg, "quote") and callable(msg.quote):
            res = msg.quote(reply_text)
            if bool(res):
                logger.info("✅ 直接引用回复成功")
                return True
    except Exception as e:
        logger.debug(f"msg.quote 失败：{e}")
    return False


def try_quote_from_cache(normalized_content: str, sender: str, reply_text: str) -> bool:
    """尝试从缓存中查找并引用回复"""
    cached_msg = find_cached_message(normalized_content, sender)
    if cached_msg:
        try:
            if hasattr(cached_msg, "quote") and callable(cached_msg.quote):
                res = cached_msg.quote(reply_text)
                if bool(res):
                    logger.info("✅ 缓存引用回复成功")
                    return True
        except Exception as e:
            logger.debug(f"缓存消息引用失败：{e}")
    return False


def try_quote_by_searching_in_subwindow(chat, original_text_for_match: str, sender: str, reply_text: str) -> bool:
    """尝试在子窗口中搜索并引用回复"""
    msgs = []
    try:
        if hasattr(chat, "GetAllMessage"):
            msgs = chat.GetAllMessage()
        else:
            msgs = wx.GetAllMessage()
    except Exception as e:
        logger.debug(f"GetAllMessage 失败：{e}")
        return False

    norm_target = normalize_spaces(strip_nick_prefix(original_text_for_match))

    # 从最新消息开始搜索
    for m in reversed(msgs):
        try:
            # 滚动到消息位置（如果需要）
            if hasattr(m, "roll_into_view") and callable(m.roll_into_view):
                try:
                    m.roll_into_view()
                    time.sleep(0.05)  # 短暂等待，确保消息可见
                except Exception:
                    pass

            mcontent_segments = get_all_texts(m)
            mcontent = normalize_spaces(" ".join(mcontent_segments))
            msender = str(getattr(m, "sender", "") or getattr(m, "author", ""))

            if normalize_spaces(strip_nick_prefix(mcontent)) == norm_target:
                if sender and msender and (msender != sender):
                    continue
                if hasattr(m, "quote") and callable(m.quote):
                    try:
                        res = m.quote(reply_text)
                        if bool(res):
                            logger.info("✅ 搜索引用回复成功")
                            return True
                    except Exception as e:
                        logger.debug(f"消息引用失败：{e}")
        except Exception:
            continue
    return False


def send_via_main_window(reply_text: str) -> bool:
    """通过主窗口发送消息（兜底方案）"""
    try:
        wx.ChatWith(who=TARGET_GROUP_NAME, exact=True)
        time.sleep(0.15)  # 减少等待时间
    except Exception as e:
        logger.error(f"ChatWith 失败：{e}")

    for i in range(SEND_RETRIES):
        try:
            wx.SendMsg(reply_text, who=None)
            logger.info("✅ 主窗口发送成功")
            return True
        except Exception as e:
            logger.warning(f"主窗口发送重试 {i+1}/{SEND_RETRIES}：{e}")
            if i < SEND_RETRIES - 1:
                time.sleep(SEND_RETRY_DELAY)
    return False


def update_stats(status: str):
    """更新统计信息"""
    with stats_lock:
        queue_stats[status] = queue_stats.get(status, 0) + 1


def consumer_worker(worker_id: int):
    """消费者线程：处理队列中的问题"""
    logger.info(f"工作线程 #{worker_id} 启动")

    while not stop_event.is_set():
        try:
            task = task_queue.get(timeout=0.5)
        except queue.Empty:
            continue

        start = time.time()
        msg = task['msg']
        chat = task['chat']
        original_text = task['original_text']
        sender = task['sender']
        question = task['question']
        normalized_content = task.get('normalized_content', '')

        try:
            def timed_out() -> bool:
                return (time.time() - start) > TASK_TIMEOUT_SEC

            if timed_out():
                logger.warning(f"[Worker#{worker_id}] ⏱️ 任务超时（启动即过时），丢弃：{question[:50]}")
                update_stats("timeout")
                continue

            logger.info(f"[Worker#{worker_id}] 🤔 处理问题：{question[:50]}...")

            # 调用 AI 服务
            answer = call_dashscope(question)

            if timed_out():
                logger.warning(f"[Worker#{worker_id}] ⏱️ 任务超时（AI调用后），丢弃：{question[:50]}")
                update_stats("timeout")
                continue

            reply_text = REPLY_TEMPLATE.format(question=question, answer=answer)

            # 三级回复策略
            success = False

            # 1. 尝试直接引用原消息对象
            if try_quote_on_message_obj(msg, reply_text):
                success = True
            # 2. 尝试从缓存中查找并引用
            elif try_quote_from_cache(normalized_content, sender, reply_text):
                success = True
            # 3. 尝试在子窗口中搜索并引用
            elif try_quote_by_searching_in_subwindow(chat, original_text, sender, reply_text):
                success = True
            # 4. 兜底：主窗口发送
            else:
                logger.info(f"[Worker#{worker_id}] ℹ️ 降级到主窗口发送")
                success = send_via_main_window(reply_text)

            if success:
                update_stats("success")
                elapsed = time.time() - start
                logger.info(f"[Worker#{worker_id}] ✅ 完成（{elapsed:.2f}s）：{question[:50]}")
            else:
                update_stats("failed")
                logger.error(f"[Worker#{worker_id}] ❌ 发送失败：{question[:50]}")

        except Exception as e:
            logger.error(f"[Worker#{worker_id}] ❌ 处理任务异常：{e}")
            update_stats("failed")
        finally:
            task_queue.task_done()


def on_message(msg: Message, chat):
    """消息回调函数"""
    try:
        if not is_target_group(chat):
            return
        if not is_group_chat(chat):
            return

        attr = getattr(msg, "attr", "")
        mtype = getattr(msg, "type", "")
        sender = str(getattr(msg, "sender", "") or getattr(msg, "author", ""))
        segs = get_all_texts(msg)

        logger.debug(f"[收到] 群={get_chat_name(chat)} attr={attr} type={mtype} sender={sender}")

        # 缓存所有群友消息
        if isinstance(msg, FriendMessage) or attr == "friend":
            cache_message(msg)

        # 严格只处理群友消息
        if not isinstance(msg, FriendMessage) and attr != "friend":
            return

        question = extract_question_from_msg(msg)
        if not question:
            return

        # 去重检查
        if not remember_question_once(question):
            logger.info(f"⚠️ 重复问题，忽略：{question[:50]}")
            return

        signature = make_message_signature(msg)
        if signature in processed_messages:
            logger.info(f"⚠️ 重复消息签名，忽略")
            return
        processed_messages.add(signature)

        original_text = normalize_spaces(" ".join(segs))
        normalized_content = normalize_spaces(strip_nick_prefix(original_text))

        # 构建任务
        task = {
            "msg": msg,
            "chat": chat,
            "original_text": original_text,
            "normalized_content": normalized_content,
            "sender": sender,
            "question": question,
        }

        # 队列满时的处理
        if task_queue.full():
            logger.warning(f"⚠️ 队列已满（{task_queue.qsize()}/{task_queue.maxsize}），丢弃问题：{question[:50]}")
            update_stats("failed")
            return

        try:
            task_queue.put(task, timeout=0.5)
            update_stats("total")
            qsize = task_queue.qsize()
            logger.info(f"📥 入队成功 [队列: {qsize}]：{question[:50]}")
        except queue.Full:
            logger.warning(f"⚠️ 任务队列已满（put失败），忽略问题：{question[:50]}")
            update_stats("failed")

    except Exception as e:
        logger.error(f"on_message 异常：{e}", exc_info=True)


def print_stats():
    """定期打印统计信息"""
    while not stop_event.is_set():
        time.sleep(60)  # 每分钟打印一次
        with stats_lock:
            if queue_stats["total"] > 0:
                logger.info(f"📊 统计 - 总计:{queue_stats['total']} "
                          f"成功:{queue_stats['success']} "
                          f"失败:{queue_stats['failed']} "
                          f"超时:{queue_stats['timeout']} "
                          f"队列:{task_queue.qsize()}")


def main():
    """主函数"""
    logger.info(f"🚀 启动微信机器人")
    logger.info(f"⚙️ 配置 - 目标群聊:{TARGET_GROUP_NAME} 触发词:{TRIGGER_PREFIX} 工作线程:{WORKERS}")

    # 启动工作线程
    for i in range(WORKERS):
        t = threading.Thread(
            target=consumer_worker,
            args=(i+1,),
            name=f"worker-{i+1}",
            daemon=True
        )
        t.start()

    # 启动统计线程
    stats_thread = threading.Thread(target=print_stats, name="stats", daemon=True)
    stats_thread.start()

    # 添加监听
    try:
        sub = wx.AddListenChat(nickname=TARGET_GROUP_NAME, callback=on_message)
        if hasattr(sub, "ChatInfo"):
            info = sub.ChatInfo() or {}
            logger.info(f"✅ 监听子窗口: {info}")
        else:
            logger.info(f"✅ 监听返回: {sub}")
    except Exception as e:
        logger.error(f"❌ AddListenChat 失败：{e}")
        stop_event.set()
        return

    # 启动监听
    try:
        if hasattr(wx, "StartListening"):
            wx.StartListening()
            logger.info("✅ 已调用 StartListening()")
    except Exception as e:
        logger.error(f"❌ StartListening 失败：{e}")

    logger.info(f"✅ 监听已启动，等待消息...")

    try:
        wx.KeepRunning()
    except KeyboardInterrupt:
        logger.info("👋 收到退出信号")
    finally:
        logger.info("🛑 正在停止...")
        stop_event.set()
        try:
            task_queue.join()
        except Exception:
            pass

        # 最终统计
        with stats_lock:
            logger.info(f"📊 最终统计 - 总计:{queue_stats['total']} "
                      f"成功:{queue_stats['success']} "
                      f"失败:{queue_stats['failed']} "
                      f"超时:{queue_stats['timeout']}")


if __name__ == "__main__":
    main()
