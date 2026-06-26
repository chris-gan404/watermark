# semi-utils / Watermark

> A photo watermarking utility for batch watermark generation, EXIF rendering, image layout processing, and export quality control.
>
> 一个用于批量添加照片水印、渲染 EXIF 信息、处理图片版式以及控制导出质量的工具。

## Features / 功能

- Batch-generate photo watermarks from reusable JSON templates.
- Render camera model, lens, focal length, aperture, shutter speed, ISO, shooting time, and brand logos from EXIF data.
- Preserve source ICC color profiles during preview conversion and final export, keeping Display P3, sRGB, and other color spaces mapped consistently.
- Parse GPS coordinates from EXIF metadata and reverse-geocode them into readable state, city, or locality text for location-aware watermarks.
- Support multiple layout styles, including classic EXIF watermarks, centered logo watermarks, blurred backgrounds, rounded corners, shadows, and social-media-friendly margins.
- Keep template files editable so custom text, logos, and styles can be adjusted without changing code.
- Provide a Flask-based local web interface for previewing and processing images.

- 支持通过可复用的 JSON 模板批量生成照片水印。
- 可从 EXIF 信息中渲染相机型号、镜头、焦距、光圈、快门、ISO、拍摄时间和品牌 Logo。
- 在预览转换和最终导出时保留源图 ICC 色彩配置，避免 Display P3、sRGB 等色彩空间映射不一致造成偏色。
- 可从 EXIF GPS 信息中解析经纬度，并反向解析为州、城市或街区等可读地点，用于带地点信息的时间水印。
- 支持多种版式：经典 EXIF 水印、居中 Logo 水印、背景模糊、圆角、阴影和适合社交媒体分享的留白样式。
- 模板文件可直接编辑，方便在不改代码的情况下调整文字、Logo 和视觉样式。
- 提供基于 Flask 的本地网页界面，用于预览和处理图片。

## Installation / 安装

Requires Python 3.13 or newer.

需要 Python 3.13 或更高版本。

```bash
pip install -r requirements.txt
```

## Usage / 使用

Start the local web app:

启动本地网页应用：

```bash
python app.py
```

Then open the local address printed in the terminal and process images through the web interface.

随后打开终端中显示的本地地址，即可在网页界面中处理图片。

Location reverse-geocoding can be configured in `config/config.ini`. Results are cached locally in `config/geocoding_cache.json` to reduce repeated network lookups.

反向解析位置信息可在 `config/config.ini` 中配置，解析结果会缓存在 `config/geocoding_cache.json`，减少重复网络查询。

## Templates / 模板

| Template / 模板 | Description / 描述 | Preview / 效果 |
| --- | --- | --- |
| [standard1](./static/standard1.json) | Classic EXIF watermark with camera model, lens, focal length, aperture, shutter speed, ISO, shooting time, and camera brand logo.<br>经典 EXIF 水印，包含相机型号、镜头、焦距、光圈、快门、ISO、拍摄时间和相机品牌 Logo。 | ![standard1](./static/standard1.jpeg) |
| [standard2](./static/standard2.json) | Adds rounded corners, shadows, and margins on top of `standard1`, suitable for social media sharing.<br>在 `standard1` 基础上添加圆角、阴影和留白，适合社交媒体分享。 | ![standard2](./static/standard2.jpeg) |
| [nikon_blur](./static/nikon_blur.json) | Nikon-style watermark with a highlighted red `Z` in the camera model and a blurred background.<br>尼康风格水印，相机型号中的红色 `Z` 高亮，并配合背景模糊效果。 | ![nikon_blur](./static/nikon_blur.jpeg) |
| [blur](./static/blur.json) | Minimal centered layout with camera model and shooting parameters over a blurred background.<br>简洁居中版式，相机型号和参数垂直居中展示，并配合背景模糊效果。 | ![blur](./static/blur.jpeg) |
| [normal1](./static/normal1.json) | Minimal lower-right shooting-parameter watermark.<br>极简风格，在右下角显示拍摄参数，低调不抢眼。 | ![normal1](./static/normal1.jpeg) |
| [normal2](./static/normal2.json) | Folder name plus shooting time with simple orange text.<br>文件夹名称加拍摄时间，橙色文字，简洁实用。 | ![normal2](./static/normal2.jpeg) |
| [center_logo](./static/center_logo.json) | Center logo watermark with customizable text around it.<br>中心 Logo 水印，可自定义四周文字内容。 | ![center_logo](./static/center_logo.jpeg) |

## Build / 打包

Build scripts and CI workflows are included under `.github/workflows`.

打包脚本和 CI 工作流位于 `.github/workflows` 目录。

## License / 许可证

This project is released under the [PolyForm Noncommercial License 1.0.0](LICENSE).

本项目基于 [PolyForm Noncommercial License 1.0.0](LICENSE) 发布。

Commercial use is prohibited unless you obtain prior written permission from the copyright holder.

未经版权方事先书面许可，禁止将本项目用于商业用途。

Permitted uses include personal study, research, testing, hobby projects, education, and other noncommercial purposes allowed by the license.

许可证允许个人学习、研究、测试、兴趣项目、教育以及其他非商业用途。

### Third-party license / 第三方协议

This project may work with [ExifTool](https://exiftool.org/). ExifTool is distributed under its own [GPL v1 + Artistic License 2.0](https://exiftool.org/#license), and its license terms are not changed by this repository's license.

本项目可能配合 [ExifTool](https://exiftool.org/) 使用。ExifTool 基于其自身的 [GPL v1 + Artistic License 2.0](https://exiftool.org/#license) 发布，本仓库的许可证不会改变 ExifTool 的原始授权条款。
