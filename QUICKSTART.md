# 🚀 Quick Start Guide

Hướng dẫn nhanh để bắt đầu sử dụng Camera Simulator trong 5 phút.

## Bước 1: Chuẩn bị video nguồn

Đặt ít nhất 1 file video vào thư mục `source_videos/`:

```bash
cd tools/camera_simulator

# Tạo thư mục nếu chưa có
mkdir -p source_videos

# Copy video mẫu của bạn vào đây
# Ví dụ:
cp /path/to/your/video.mp4 source_videos/test.mp4
```

Hoặc nếu chưa có video, tạo một video test đơn giản bằng FFmpeg:
```bash
ffmpeg -f lavfi -i testsrc=duration=30:size=640x480:rate=10 -pix_fmt yuv420p source_videos/test.mp4 -y
```

## Bước 2: Chạy thử nghiệm (Quick Test)

Chạy với cấu hình test có sẵn (không cần chỉnh sửa gì):

```bash
python simulator.py -c quick_test.yaml
```

Bạn sẽ thấy simulator bắt đầu tạo video trong thư mục `output/TestCam1` và `output/TestCam2`.

## Bước 3: Cấu hình cho Production

1. Copy file config mẫu:
   ```bash
   cp config.example.yaml config.yaml
   ```

2. Sửa `config.yaml`:
   - Thay đổi `source_video` thành đường dẫn video của bạn
   - Chỉnh `output_folder` trỏ đến thư mục input của ứng dụng (VD: `../../backend/input/Cam1`)
   - Chọn pattern phù hợp (`continuous`, `motion_triggered`, v.v.)

3. Chạy:
   ```bash
   python simulator.py -c config.yaml
   ```
