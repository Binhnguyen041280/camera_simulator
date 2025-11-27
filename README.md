# 📹 Camera Simulator

Công cụ mô phỏng camera phát sinh video liên tục để test ứng dụng xử lý video trong điều kiện thực tế.

## 🎯 Mục đích

Trong quá trình phát triển, bạn chỉ có vài file video mẫu để test → batch xử lý nhanh xong. Nhưng trong thực tế:
- Camera hoạt động **24/7** liên tục
- Có **nhiều camera** đồng thời
- Camera có thể **bật/tắt** không đều
- Thời lượng video **thay đổi** (10 phút, 20 phút, ...)
- Camera chỉ ghi khi **có chuyển động/sự kiện**

**Camera Simulator** giúp bạn:
- ✅ Mô phỏng camera phát sinh video liên tục
- ✅ Test khả năng xử lý real-time của ứng dụng
- ✅ Đánh giá hiệu năng với nhiều camera
- ✅ Kiểm tra batch scheduler trong điều kiện thực tế
- ✅ Metadata timestamp chính xác (thời gian thực)

## 🚀 Cài đặt

1. Clone repository:
```bash
git clone https://github.com/Binhnguyen041280/camera_simulator.git
cd camera_simulator
```

2. Cài đặt dependencies:
```bash
pip install -r requirements.txt
```

3. Cài đặt FFmpeg (nếu chưa có):
- Mac: `brew install ffmpeg`
- Linux: `sudo apt install ffmpeg`

## 📖 Hướng dẫn sử dụng

### 1. Chuẩn bị video nguồn
Tạo thư mục `source_videos` và copy ít nhất 1 video vào đó:
```bash
mkdir source_videos
cp /path/to/your/video.mp4 source_videos/test.mp4
```

### 2. Cấu hình
Copy file config mẫu:
```bash
cp config.example.yaml config.yaml
```
Chỉnh sửa `config.yaml` để thiết lập các camera và pattern mong muốn.

### 3. Chạy Simulator
```bash
python simulator.py -c config.yaml
```

## ⚙️ Recording Patterns

Simulator hỗ trợ 4 kiểu ghi hình:

1. **continuous**: Ghi liên tục, video nối tiếp nhau (VD: Camera an ninh).
2. **motion_triggered**: Ghi khi có chuyển động, xen kẽ thời gian nghỉ (VD: Camera hành lang).
3. **event_triggered**: Ghi khi có sự kiện, thời gian nghỉ dài hơn (VD: Camera dây chuyền sản xuất).
4. **random_on_off**: Bật/tắt ngẫu nhiên trong ngày.

## 📂 Cấu trúc Output

Video sẽ được tạo trong thư mục `output/{CameraName}/` với định dạng:
`{CameraName}_{YYYYMMDD}_{HHMMSS}.mp4`

Ví dụ: `output/Cam1/Cam1_20251120_103000.mp4`
