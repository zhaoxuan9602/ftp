"""
    ftp 文件服务器
    并发网络功能训练
"""

from socket import *
from threading import Thread
import os,time

# 全局变量
ADDR = ("176.215.155.161",8888)
FTP = "/home/tarena/ftp/" # 文件库路径

#将客户端请求功能封装为类
class FtpServer:
    def __init__(self,connfd,FTP_PATH):
        self.connfd = connfd
        self.path = FTP_PATH
    def do_list(self):
        #获取文件列表
        files = os.listdir(self.path)
        if not files:
            self.connfd.send("该文件类别为空".encode())
            return
        else:
            self.connfd.send(b"OK")
            time.sleep(0.1) # 防止粘包
        fs = ""
        for file in files:
            if file[0] != "." and \
                    os.path.isfile(self.path+file):
                fs +=file + '\n'#人为添加消息边界,防止粘包
        self.connfd.send(fs.encode())

    def do_get(self,filename):
        try :
            fd = open(self.path +filename,'rb')
        except Exception:
            self.connfd.send("文件不存在".encode())
            return
        else:
            self.connfd.send(b"OK")
            time.sleep(0.1)
        while True:
            data = fd.read(1024)
            if  not data:
                time.sleep(0.1)
                self.connfd.send(b"##")
                break
            self.connfd.send(data)
    def do_put(self,filename):
        if  os.path.exists(self.path+filename):
            self.connfd.send("该文件已存在".encode())
            return
        self.connfd.send(b"OK")
        fd = open(self.path+filename,'wb')
        while True:
            data = self.connfd.recv(1024)
            if data == b"##":
                break
            fd.write(data)
        fd.close()

def handle(connfd):
    # 选择文件夹
    cls = connfd.recv(1024).decode()
    FTP_PATH = FTP +cls +'/'
    ftp =FtpServer(connfd,FTP_PATH)
    while True:
        # 接收客户端请求
        data = connfd.recv(1024).decode()
        # 如果客户端断开返回data 为空
        if not data or data[0] == "Q":
            return
        elif data[0] == "L":#只有一个字母所以第一个字母就是L
            ftp.do_list()
        elif data[0] == "G":
            filename = data.split(" ")[-1]
            ftp.do_get(filename)
        elif data[0] == "P":
            filename = data.split(" ")[-1]
            ftp.do_put(filename)

#网络搭建
def main():
    s = socket(AF_INET,SOCK_STREAM)
    s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    s.bind(ADDR)
    s.listen(5)
    print("Listen the port 8888 ...")
    while True:
        try:
            connfd, addr = s.accept()
        except KeyboardInterrupt:
            print("退出服务程序")
            return
        except Exception as e:
            print(e)
            continue  # 退到try
        print("连接的客户端:",addr)
        # 创建新的线程处理客户端请求
        client = Thread(target=handle, args=(connfd,))
        client.setDaemon(True)  # 不能用join是因为要循环接收客户端请求,设置分之线程随主线程退出
        client.start()

if __name__ == "__main__":
    main()