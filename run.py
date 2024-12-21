import subprocess
import sys
import os
import signal
import time
import logging
import asyncio
from threading import Thread
from queue import Queue, Empty

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def enqueue_output(out, queue):
    """Add output lines to queue."""
    try:
        for line in iter(out.readline, ''):
            queue.put(line)
    except (ValueError, IOError) as e:
        logger.debug(f"Stream closed: {str(e)}")
    finally:
        try:
            out.close()
        except:
            pass

class SatoriApp:
    def __init__(self):
        self.backend_process = None
        self.frontend_process = None
        self.is_running = False
        self.backend_queue = Queue()
        self.frontend_queue = Queue()

    def start(self):
        """Start both backend and frontend servers."""
        try:
            logger.info("🚀 Starting SATORI AI...")
            
            # Start backend server with uvicorn
            logger.info("📡 Starting backend server...")
            self.backend_process = subprocess.Popen(
                ["uvicorn", "backend.api.main:app", "--host", "0.0.0.0", "--port", "8000"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
            )
            
            # Start output threads
            Thread(target=enqueue_output, 
                  args=(self.backend_process.stdout, self.backend_queue), 
                  daemon=True).start()
            Thread(target=enqueue_output, 
                  args=(self.backend_process.stderr, self.backend_queue), 
                  daemon=True).start()
            
            # Wait for backend to start and check if it's still running
            time.sleep(2)
            if self.backend_process.poll() is not None:
                # Backend failed to start
                self.dump_process_output()
                logger.error("❌ Backend server failed to start!")
                self.stop()
                return
            
            # Start frontend server with environment variable to disable signal handling
            logger.info("🎨 Starting frontend server...")
            env = os.environ.copy()
            env['STREAMLIT_DISABLE_SIGNAL_HANDLERS'] = 'true'
            
            self.frontend_process = subprocess.Popen(
                [sys.executable, "-m", "streamlit", "run", "frontend/app.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True,
                env=env,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
            )
            
            # Start output threads for frontend
            Thread(target=enqueue_output, 
                  args=(self.frontend_process.stdout, self.frontend_queue), 
                  daemon=True).start()
            Thread(target=enqueue_output, 
                  args=(self.frontend_process.stderr, self.frontend_queue), 
                  daemon=True).start()
            
            self.is_running = True
            logger.info("✨ SATORI AI is running!")
            
            # Keep the script running and monitor the processes
            while self.is_running:
                # Check backend process
                if self.backend_process.poll() is not None:
                    # Get any remaining output from queues
                    self.read_process_output()
                    logger.error("❌ Backend server stopped unexpectedly!")
                    self.stop()
                    break
                
                # Check frontend process
                if self.frontend_process.poll() is not None:
                    # Get any remaining output from queues
                    self.read_process_output()
                    logger.error("❌ Frontend server stopped unexpectedly!")
                    self.stop()
                    break
                
                # Read output (non-blocking)
                self.read_process_output()
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            logger.info("👋 Received shutdown signal...")
            self.stop()
        except Exception as e:
            logger.error(f"❌ Error starting SATORI AI: {str(e)}")
            self.stop()
            raise

    def read_process_output(self):
        """Read and log output from processes."""
        try:
            # Read backend output
            while True:
                try:
                    line = self.backend_queue.get_nowait()
                    if line:
                        logger.info(f"[Backend] {line.strip()}")
                except Empty:
                    break
            
            # Read frontend output
            while True:
                try:
                    line = self.frontend_queue.get_nowait()
                    if line:
                        logger.info(f"[Frontend] {line.strip()}")
                except Empty:
                    break
        except Exception as e:
            logger.error(f"Error reading process output: {str(e)}")

    def dump_process_output(self):
        """Dump all remaining process output."""
        # Dump backend output
        if self.backend_process:
            try:
                # Try to get any remaining output from the queue first
                while True:
                    try:
                        line = self.backend_queue.get_nowait()
                        if line:
                            logger.info(f"[Backend] {line.strip()}")
                    except Empty:
                        break
            except Exception as e:
                logger.debug(f"Error reading backend queue: {str(e)}")

        # Dump frontend output
        if self.frontend_process:
            try:
                # Try to get any remaining output from the queue first
                while True:
                    try:
                        line = self.frontend_queue.get_nowait()
                        if line:
                            logger.info(f"[Frontend] {line.strip()}")
                    except Empty:
                        break
            except Exception as e:
                logger.debug(f"Error reading frontend queue: {str(e)}")

    def stop(self):
        """Stop both servers gracefully."""
        logger.info("🔄 Shutting down SATORI AI...")
        
        # Stop frontend
        if self.frontend_process:
            logger.info("Stopping frontend server...")
            try:
                self.frontend_process.terminate()
                self.frontend_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.frontend_process.kill()
        
        # Stop backend
        if self.backend_process:
            logger.info("Stopping backend server...")
            try:
                self.backend_process.terminate()
                self.backend_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.backend_process.kill()
        
        self.is_running = False
        logger.info("✅ Shutdown complete!")

def main():
    # Register signal handlers in the main thread
    def signal_handler(signum, frame):
        """Handle system signals."""
        logger.info(f"Received signal {signum}")
        if app.is_running:
            app.stop()
            sys.exit(0)

    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Create and start the application
    global app
    app = SatoriApp()
    app.start()

if __name__ == "__main__":
    main() 