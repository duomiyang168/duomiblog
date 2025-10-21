# Raphael AI Clone - Free AI Image Generator

这是一个复刻 [raphael.app](https://raphael.app/) 的项目，使用现代化的技术栈构建。

## 技术栈

- **Next.js 15** (App Router) - React 框架
- **TypeScript** - 类型安全
- **Tailwind CSS** - 样式框架
- **shadcn/ui** - UI 组件库
- **Lucide React** - 图标库

## 功能特性

- ✨ 简洁现代的用户界面
- 🎨 AI 图像生成模拟器
- 📱 完全响应式设计
- 🚀 无需注册即可使用
- 🖼️ 图像画廊展示
- 💾 图像下载功能
- 📋 功能特点展示
- ❓ 常见问题解答

## 快速开始

### 安装依赖

```bash
npm install
```

### 开发模式

```bash
npm run dev
```

然后在浏览器中打开 [http://localhost:3000](http://localhost:3000)

### 构建生产版本

```bash
npm run build
```

### 运行生产版本

```bash
npm start
```

## 项目结构

```
├── app/                    # Next.js App Router 目录
│   ├── layout.tsx         # 根布局
│   ├── page.tsx           # 主页
│   └── globals.css        # 全局样式
├── components/            # React 组件
│   ├── ui/               # shadcn/ui 组件
│   ├── navbar.tsx        # 导航栏
│   ├── hero-section.tsx  # 主标题区域
│   ├── image-generator.tsx   # 图像生成器
│   ├── features-section.tsx  # 功能特点
│   ├── faq-section.tsx   # FAQ 区域
│   └── footer.tsx        # 页脚
├── lib/                   # 工具函数
│   └── utils.ts          # 通用工具
└── public/               # 静态资源

```

## 注意事项

- 当前图像生成功能使用 Lorem Picsum 提供模拟图像
- 如需集成真实 AI 图像生成 API，请修改 `components/image-generator.tsx` 中的 `handleGenerate` 函数
- 建议集成如 Replicate API、Stability AI 或其他图像生成服务

## 自定义

### 修改颜色主题

编辑 `app/globals.css` 中的 CSS 变量来自定义颜色方案。

### 添加真实 AI API

在 `components/image-generator.tsx` 中找到 `handleGenerate` 函数，替换模拟代码为真实的 API 调用：

```typescript
const handleGenerate = async () => {
  if (!prompt.trim()) return;

  setIsGenerating(true);

  try {
    // 调用你的 AI API
    const response = await fetch('/api/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt })
    });

    const data = await response.json();

    const newImage: GeneratedImage = {
      id: Date.now().toString(),
      url: data.imageUrl,
      prompt: prompt,
      timestamp: Date.now(),
    };

    setGeneratedImages((prev) => [newImage, ...prev]);
  } catch (error) {
    console.error('Generation failed:', error);
  } finally {
    setIsGenerating(false);
  }
};
```

## 开源协议

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！
