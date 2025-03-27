import sys
import cv2
import json
import os
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QTime
from PyQt5.QtGui import QImage, QPixmap, QIcon, QPainter, QPen, QColor
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QSlider, QLabel, QPushButton, 
                             QFileDialog, QSplitter, QStyle)

def create_loop_icon(size, enabled=True):
    """Create a custom loop icon with the specified size and state"""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)
    
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    
    # Set up the pen with appropriate thickness
    pen = QPen(QColor(0, 0, 0))
    pen.setWidth(2)
    painter.setPen(pen)
    
    # Calculate dimensions
    margin = size // 4
    width = size - 2 * margin
    height = size - 2 * margin
    
    # Draw the oval
    painter.drawEllipse(margin, margin, width, height)
    
    # Draw the loop arrows
    arrow_size = size // 4
    center_x = size // 2
    center_y = size // 2
    
    # Draw a single arrow that follows the oval path
    painter.save()
    painter.translate(center_x, center_y)
    
    # Draw the arrow shaft following the oval path
    painter.drawArc(margin, margin, width, height, 0, 5760)  # 5760 = 16 * 360 (full circle)
    
    # Draw the arrow head
    painter.rotate(45)  # Position arrow head at 45 degrees
    painter.drawLine(0, -arrow_size//2, arrow_size//2, 0)
    painter.drawLine(0, -arrow_size//2, -arrow_size//2, 0)
    painter.drawLine(0, -arrow_size//2, 0, arrow_size//2)
    
    painter.restore()
    
    # If disabled, draw a slash through the icon
    if not enabled:
        pen.setWidth(3)
        painter.setPen(pen)
        painter.drawLine(margin, margin + height, margin + width, margin)
    
    painter.end()
    return QIcon(pixmap)

class VideoPlayer(QWidget):
    """Component for displaying and controlling a single video"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.cap = None
        self.current_frame = 0
        self.total_frames = 0
        self.fps = 0
        self.width = 0
        self.height = 0
        self.duration = 0
        self.filepath = ""  # Store full filepath
        self.filename = ""  # Store just the filename for display
        
        self.initUI()
        
    def initUI(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)  # Remove margins for better scaling
        
        # Video display area
        self.video_label = QLabel()
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setStyleSheet("background-color: black;")
        self.video_label.setMinimumSize(320, 240)  # Minimum size for video display
        
        # Info label for video statistics
        self.info_label = QLabel("No video loaded")
        self.info_label.setAlignment(Qt.AlignCenter)
        self.info_label.setStyleSheet("background-color: #f0f0f0; padding: 5px;")  # Better visibility
        self.info_label.setWordWrap(True)  # Allow text to wrap if filename is long
        
        self.layout.addWidget(self.video_label, stretch=1)  # Make video label expand
        self.layout.addWidget(self.info_label, stretch=0)  # Keep info label at fixed size
        
    def get_current_frame(self):
        """Get the current frame as a QPixmap"""
        if self.cap and 0 <= self.current_frame < self.total_frames:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.current_frame)
            ret, frame = self.cap.read()
            if ret:
                # Convert the frame from BGR to RGB for display
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb_frame.shape
                bytes_per_line = ch * w
                
                # Create QImage from the frame data
                q_img = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
                
                # Create and return QPixmap
                return QPixmap.fromImage(q_img)
        return None
    
    def load_video(self, filepath):
        if filepath:
            self.cap = cv2.VideoCapture(filepath)
            if self.cap.isOpened():
                self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
                self.fps = self.cap.get(cv2.CAP_PROP_FPS)
                self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                self.duration = self.total_frames / self.fps
                self.filepath = filepath  # Store full filepath
                self.filename = os.path.basename(filepath)  # Get just the filename
                
                # Update info label with video statistics
                self.update_info()
                
                # Show first frame
                self.show_frame(0)
                return True
        return False
    
    def update_info(self):
        """Updates the info label with video metadata"""
        if self.cap:
            self.info_label.setText(
                f"File: {self.filename}\n"
                f"Size: {self.width}x{self.height} | {self.fps:.2f} FPS | {self.duration:.2f}s"
            )
        else:
            self.info_label.setText("No video loaded")
            self.filename = ""
    
    def show_frame(self, frame_num):
        """Display the specified frame"""
        if self.cap and 0 <= frame_num < self.total_frames:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
            ret, frame = self.cap.read()
            if ret:
                self.current_frame = frame_num
                
                # Convert the frame from BGR to RGB for display
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb_frame.shape
                bytes_per_line = ch * w
                
                # Create QImage from the frame data
                q_img = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
                
                # Get the available size for the video label
                label_size = self.video_label.size()
                
                # Scale the image to fit the label while maintaining aspect ratio
                pixmap = QPixmap.fromImage(q_img)
                scaled_pixmap = pixmap.scaled(label_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                
                # Center the scaled image
                self.video_label.setPixmap(scaled_pixmap)
                return True
        return False
    
    def resizeEvent(self, event):
        """Handle resize events to update frame display"""
        super().resizeEvent(event)
        if self.cap:
            # Use QTimer to delay the frame update slightly to avoid flickering
            QTimer.singleShot(50, lambda: self.show_frame(self.current_frame))


class OverlayView(QWidget):
    """Widget for displaying one video overlaid on another with a draggable divider"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.video1 = None  # Top video
        self.video2 = None  # Bottom video
        self.divider_pos = 0.5  # Initial position (50% from left)
        self.dragging = False
        self.setMouseTracking(True)
        
    def set_videos(self, video1, video2):
        """Set the two videos to be displayed"""
        self.video1 = video1
        self.video2 = video2
        
    def paintEvent(self, event):
        """Handle painting of the overlay view"""
        if not self.video1 or not self.video2:
            return
            
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Get the current frames
        frame1 = self.video1.get_current_frame()
        frame2 = self.video2.get_current_frame()
        
        if frame1 is None or frame2 is None:
            return
            
        # Calculate dimensions
        width = self.width()
        height = self.height()
        
        # Scale frames to fit the widget while maintaining aspect ratio
        scaled_frame1 = frame1.scaled(width, height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        scaled_frame2 = frame2.scaled(width, height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        
        # Calculate positions to center the frames
        x1 = (width - scaled_frame1.width()) // 2
        y1 = (height - scaled_frame1.height()) // 2
        x2 = (width - scaled_frame2.width()) // 2
        y2 = (height - scaled_frame2.height()) // 2
        
        # Calculate the actual divider position based on the scaled frame
        divider_x = x1 + int(scaled_frame1.width() * self.divider_pos)
        
        # Draw the frames
        painter.drawPixmap(x2, y2, scaled_frame2)  # Draw bottom video full size
        painter.drawPixmap(x1, y1, scaled_frame1, 0, 0, divider_x - x1, height)  # Draw top video up to divider
        
        # Draw the divider line
        pen = QPen(QColor(255, 255, 255))
        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawLine(divider_x, 0, divider_x, height)
        
        # Draw the handle
        handle_width = 10
        handle_height = 40
        handle_x = divider_x - handle_width // 2
        handle_y = (height - handle_height) // 2
        
        # Draw handle background
        painter.fillRect(handle_x, handle_y, handle_width, handle_height, QColor(255, 255, 255))
        
        # Draw handle border
        painter.setPen(QPen(QColor(0, 0, 0)))
        painter.drawRect(handle_x, handle_y, handle_width, handle_height)
        
    def mousePressEvent(self, event):
        """Handle mouse press events for dragging"""
        if event.button() == Qt.LeftButton:
            # Get the scaled frame dimensions
            if self.video1 and self.video2:
                frame1 = self.video1.get_current_frame()
                if frame1:
                    scaled_frame1 = frame1.scaled(self.width(), self.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    x1 = (self.width() - scaled_frame1.width()) // 2
                    divider_x = x1 + int(scaled_frame1.width() * self.divider_pos)
                    
                    handle_width = 10
                    handle_height = 40
                    handle_x = divider_x - handle_width // 2
                    handle_y = (self.height() - handle_height) // 2
                    
                    # Check if click is within handle area
                    if (handle_x <= event.x() <= handle_x + handle_width and 
                        handle_y <= event.y() <= handle_y + handle_height):
                        self.dragging = True
            
    def mouseReleaseEvent(self, event):
        """Handle mouse release events"""
        if event.button() == Qt.LeftButton:
            self.dragging = False
            
    def mouseMoveEvent(self, event):
        """Handle mouse move events for dragging"""
        if self.dragging and self.video1:
            frame1 = self.video1.get_current_frame()
            if frame1:
                scaled_frame1 = frame1.scaled(self.width(), self.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                x1 = (self.width() - scaled_frame1.width()) // 2
                # Calculate divider position relative to the scaled frame
                relative_x = event.x() - x1
                self.divider_pos = max(0.0, min(1.0, relative_x / scaled_frame1.width()))
                self.update()  # Trigger repaint


class VideoComparisonApp(QMainWindow):
    """Main application window for video comparison"""
    
    def __init__(self):
        super().__init__()
        self.video_player1 = VideoPlayer()
        self.video_player2 = VideoPlayer()
        self.overlay_view = OverlayView()
        self.playing = False
        self.looping = False  # Track loop state
        self.play_timer = QTimer()
        self.play_timer.timeout.connect(self.update_frame)
        self.current_frame = 0  # Track current frame directly
        self.preferences_file = "video_preferences.json"
        self.is_overlay_mode = False  # Track current display mode
        
        self.initUI()
        self.load_preferences()  # Load last played videos
    
    def initUI(self):
        self.setWindowTitle('Video Comparison Tool')
        self.setGeometry(100, 100, 1200, 700)
        self.setMinimumSize(800, 600)  # Set minimum window size
        
        # Central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)  # Add some padding around the edges
        
        # Create a horizontal layout for side-by-side view
        self.side_by_side_layout = QHBoxLayout()
        self.side_by_side_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins
        self.side_by_side_layout.addWidget(self.video_player1)
        self.side_by_side_layout.addWidget(self.video_player2)
        
        # Create a container widget for side-by-side layout
        self.side_by_side_container = QWidget()
        self.side_by_side_container.setLayout(self.side_by_side_layout)
        
        # Initially hide the overlay view
        self.overlay_view.hide()
        
        # Controls layout
        controls_layout = QHBoxLayout()
        controls_layout.setContentsMargins(0, 5, 0, 5)  # Add some vertical padding
        
        # Load buttons
        self.load_btn1 = QPushButton("Load Video 1")
        self.load_btn1.clicked.connect(lambda: self.load_video(1))
        self.load_btn2 = QPushButton("Load Video 2")
        self.load_btn2.clicked.connect(lambda: self.load_video(2))
        
        # Play/pause button with icons
        self.play_btn = QPushButton()
        self.play_btn.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.play_btn.setIconSize(self.play_btn.size())
        self.play_btn.setFixedSize(40, 40)  # Fixed size for the button
        self.play_btn.clicked.connect(self.toggle_play)
        self.play_btn.setEnabled(False)
        
        # Loop toggle button with custom icons
        self.loop_btn = QPushButton()
        self.loop_btn.setFixedSize(40, 40)  # Fixed size for the button
        self.loop_btn.setToolTip("Toggle Loop")
        self.loop_btn.clicked.connect(self.toggle_loop)
        self.loop_btn.setEnabled(False)
        self.update_loop_icon()  # Set initial icon
        
        # Mode toggle button
        self.mode_btn = QPushButton("Switch to Overlay")
        self.mode_btn.clicked.connect(self.toggle_mode)
        self.mode_btn.setEnabled(False)
        
        # Timeline slider
        self.timeline_slider = QSlider(Qt.Horizontal)
        self.timeline_slider.setMinimum(0)
        self.timeline_slider.setMaximum(1000)  # Will be adjusted when videos are loaded
        self.timeline_slider.valueChanged.connect(self.slider_value_changed)
        self.timeline_slider.setEnabled(False)
        
        # Current time display
        self.time_label = QLabel("00:00 / 00:00")
        self.time_label.setMinimumWidth(100)  # Prevent time label from shrinking
        
        # Add widgets to controls layout
        controls_layout.addWidget(self.load_btn1)
        controls_layout.addWidget(self.load_btn2)
        controls_layout.addWidget(self.play_btn)
        controls_layout.addWidget(self.loop_btn)
        controls_layout.addWidget(self.mode_btn)
        controls_layout.addWidget(self.timeline_slider, stretch=1)  # Make slider expand
        controls_layout.addWidget(self.time_label)
        
        # Add layouts to main layout
        main_layout.addWidget(self.side_by_side_container, stretch=1)  # Make video area expand
        main_layout.addWidget(self.overlay_view, stretch=1)  # Add overlay view
        main_layout.addLayout(controls_layout, stretch=0)  # Keep controls at fixed size
        
    def save_preferences(self):
        """Save the current video paths to preferences file"""
        preferences = {
            "video1_path": self.video_player1.filepath if self.video_player1.cap else "",
            "video2_path": self.video_player2.filepath if self.video_player2.cap else ""
        }
        try:
            with open(self.preferences_file, 'w') as f:
                json.dump(preferences, f)
        except Exception as e:
            print(f"Error saving preferences: {e}")
    
    def load_preferences(self):
        """Load the last played video paths from preferences file"""
        try:
            if os.path.exists(self.preferences_file):
                with open(self.preferences_file, 'r') as f:
                    preferences = json.load(f)
                    
                # Load video 1 if path exists
                if preferences.get("video1_path") and os.path.exists(preferences["video1_path"]):
                    self.video_player1.load_video(preferences["video1_path"])
                
                # Load video 2 if path exists
                if preferences.get("video2_path") and os.path.exists(preferences["video2_path"]):
                    self.video_player2.load_video(preferences["video2_path"])
                
                # Enable controls if both videos are loaded
                if self.video_player1.cap is not None and self.video_player2.cap is not None:
                    self.play_btn.setEnabled(True)
                    self.loop_btn.setEnabled(True)
                    self.timeline_slider.setEnabled(True)
                    self.mode_btn.setEnabled(True)  # Enable mode button when both videos are loaded
                    max_frames = min(self.video_player1.total_frames, self.video_player2.total_frames)
                    self.timeline_slider.setMaximum(max_frames - 1)
                    self.update_time_label(0)
        except Exception as e:
            print(f"Error loading preferences: {e}")
    
    def load_video(self, player_num):
        """Load a video file for the specified player"""
        filepath, _ = QFileDialog.getOpenFileName(
            self,
            f"Select Video {player_num}",
            "",
            "Video Files (*.mp4 *.avi *.mkv *.mov);;All Files (*.*)"
        )
        
        if filepath:
            if player_num == 1:
                self.video_player1.load_video(filepath)
            else:
                self.video_player2.load_video(filepath)
                    
            # Update timeline slider range and enable controls if both videos are loaded
            if self.video_player1.cap and self.video_player2.cap:
                min_frames = min(self.video_player1.total_frames, self.video_player2.total_frames)
                self.timeline_slider.setMaximum(min_frames - 1)
                self.timeline_slider.setEnabled(True)
                self.play_btn.setEnabled(True)
                self.loop_btn.setEnabled(True)
                self.mode_btn.setEnabled(True)  # Only enable mode button when both videos are loaded
                
            self.save_preferences()
    
    def slider_value_changed(self):
        """Handle timeline slider movement"""
        if self.playing:
            self.toggle_play()  # Pause playback during scrubbing
            
        self.current_frame = self.timeline_slider.value()
        self.video_player1.show_frame(self.current_frame)
        self.video_player2.show_frame(self.current_frame)
        self.update_time_label(self.current_frame)
        
        # Update overlay view if in overlay mode
        if self.is_overlay_mode:
            self.overlay_view.update()
    
    def toggle_play(self):
        """Toggle between play and pause states"""
        if not self.playing:
            # If we're at the end of the video and not looping, restart from beginning
            if self.current_frame >= self.timeline_slider.maximum() and not self.looping:
                self.current_frame = 0
                self.timeline_slider.blockSignals(True)
                self.timeline_slider.setValue(0)
                self.timeline_slider.blockSignals(False)
                self.video_player1.show_frame(0)
                self.video_player2.show_frame(0)
                self.update_time_label(0)
            
            # Start playback
            self.play_btn.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
            self.play_btn.setIconSize(self.play_btn.size())
            # Set timer interval based on video FPS
            interval = int(1000.0 / self.video_player1.fps)  # Convert FPS to milliseconds
            self.play_timer.start(interval)
            self.playing = True
        else:
            # Pause playback
            self.play_btn.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
            self.play_btn.setIconSize(self.play_btn.size())
            self.play_timer.stop()
            self.playing = False
    
    def update_loop_icon(self):
        """Update the loop button icon based on current state"""
        icon = create_loop_icon(32, self.looping)
        self.loop_btn.setIcon(icon)
        self.loop_btn.setIconSize(self.loop_btn.size())
    
    def toggle_loop(self):
        """Toggle loop mode"""
        self.looping = not self.looping
        # Update button appearance to show loop state
        if self.looping:
            self.loop_btn.setStyleSheet("background-color: #90EE90;")  # Light green background
            self.loop_btn.setToolTip("Loop Enabled")
        else:
            self.loop_btn.setStyleSheet("")  # Default background
            self.loop_btn.setToolTip("Loop Disabled")
        self.update_loop_icon()  # Update the icon
    
    def update_frame(self):
        """Update frames during playback"""
        if not self.playing:
            return
            
        next_frame = self.current_frame + 1
        
        # Check if we're at the end of the video
        if next_frame > self.timeline_slider.maximum():
            if self.looping:
                # Loop back to start
                next_frame = 0
            else:
                self.toggle_play()  # Stop playing
                return
        
        # Update the frame directly without triggering slider signal
        self.current_frame = next_frame
        self.timeline_slider.blockSignals(True)  # Block slider signals
        self.timeline_slider.setValue(next_frame)
        self.timeline_slider.blockSignals(False)  # Unblock slider signals
        
        # Update frames and time label directly
        self.video_player1.show_frame(next_frame)
        self.video_player2.show_frame(next_frame)
        self.update_time_label(next_frame)
        
        # Update overlay view if in overlay mode
        if self.is_overlay_mode:
            self.overlay_view.update()
    
    def update_time_label(self, frame_num):
        """Update the time display label based on current frame"""
        if self.video_player1.cap and self.video_player2.cap:
            fps = self.video_player1.fps  # Assuming same FPS
            current_time = frame_num / fps
            total_time = min(self.video_player1.duration, self.video_player2.duration)
            
            # Format as MM:SS
            current_mm = int(current_time // 60)
            current_ss = int(current_time % 60)
            total_mm = int(total_time // 60)
            total_ss = int(total_time % 60)
            
            self.time_label.setText(f"{current_mm:02d}:{current_ss:02d} / {total_mm:02d}:{total_ss:02d}")
    
    def toggle_mode(self):
        """Switch between side-by-side and overlay modes"""
        print("Toggle mode called")  # Debug print
        self.is_overlay_mode = not self.is_overlay_mode
        print(f"New mode: {'overlay' if self.is_overlay_mode else 'side-by-side'}")  # Debug print
        
        if self.is_overlay_mode:
            # Switch to overlay mode
            print("Switching to overlay mode")  # Debug print
            self.side_by_side_container.hide()
            self.overlay_view.set_videos(self.video_player1, self.video_player2)
            self.overlay_view.show()
            self.mode_btn.setText("Switch to Side-by-Side")
            # Force an update of the overlay view
            self.overlay_view.update()
        else:
            # Switch to side-by-side mode
            print("Switching to side-by-side mode")  # Debug print
            self.overlay_view.hide()
            self.side_by_side_container.show()
            self.mode_btn.setText("Switch to Overlay")
            
        # Update the layout
        self.centralWidget().layout().update()
        # Force a repaint of the entire window
        self.update()
    
    def closeEvent(self, event):
        """Clean up resources when the application closes"""
        if self.video_player1.cap:
            self.video_player1.cap.release()
        if self.video_player2.cap:
            self.video_player2.cap.release()
        event.accept()


if __name__ == "__main__":
    # Enable High DPI scaling
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    app = QApplication(sys.argv)
    window = VideoComparisonApp()
    window.show()
    sys.exit(app.exec_()) 