#### 基础知识
1. threading.Event()
    - threading.Event() 是 Python 线程模块中的一个同步原语,主要用于线程之间的通信。它可以被看作是一个简单的"开关"或"信号",允许一个线程向其他线程发送信号。
    - 主要方法:
        - set(): 将事件设置为 True,通知所有等待的线程。
        - clear(): 将事件设置为 False,取消所有等待的线程。
        - is_set(): 返回事件的状态,True 表示事件被设置,False 表示事件未被设置。
        - wait(timeout=None): 等待事件被设置,如果事件被设置,则立即返回;如果事件未被设置,则等待 timeout 秒后返回。
    ```
    import threading
    import time

    def worker(event):
    while not event.is_set():
        print("工作中...")
        time.sleep(1)
        print("收到停止信号,工作结束")

    # 创建事件对象
    stop_event = threading.Event()

    # 创建并启动工作线程
    thread = threading.Thread(target=worker, args=(stop_event,))
    thread.start()

    # 主线程继续执行5秒
    time.sleep(5)

    # 发送停止信号
    print("发送停止信号")
    stop_event.set()

    # 等待工作线程结束
    thread.join()

    print("程序结束")
    ```