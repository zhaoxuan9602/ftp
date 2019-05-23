from socket import *
import sys
import time

# 具体功能
class FtpClient:
    def __init__(self,sockfd):
        self.sockfd = sockfd
    def do_list(self):
        self.sockfd.send(b"L")#发送请求
        # 等待回复
        data = self.sockfd.recv(128).decode()
        if data == "OK":
            # 文件大小设置很大时可能一次接收完成,用循环会导致阻塞
            data = self.sockfd.recv(4096)
            print(data.decode())
        else:
            print(data)
    def do_quit(self):
        self.sockfd.send(b"Q")
        self.sockfd.close()
        sys.exit("谢谢使用")

    def  do_get(self,filename):
        self.sockfd.send(("G "+filename).encode())
        data = self.sockfd.recv(128).decode()
        if data == "OK":
            fd = open(filename,'wb')
            #接收内容写入文件
            while True:
                data = self.sockfd.recv(1024)
                if  data == b"##":
                    break
                fd.write(data)
            fd.close()
        else:
            print(data)


    def do_put(self,filename):
        try:
            fd = open(filename,'rb')
        except Exception:
            print("没有该文件")
            return
        filename= filename.split('/')[-1]
        self.sockfd.send(("P" + filename).encode())
        data = self.sockfd.recv(128).decode()
        if data == 'OK':
            while True:
                data = fd.read(1024)
                if not data:
                    time.sleep(0.1)
                    self.sockfd.send(b"##")
                    break
                self.sockfd.send(data)
            fd.close()
        else:
            print(data)
# 发起请求
def request(sockfd):
    ftp = FtpClient(sockfd)
    while True:
        print("\n*******************命令选项**************************")
        print("*********************view list**********************")
        print("*********************get file***********************")
        print("*********************put file***********************")
        print("*********************** quit ***********************")
        print("****************************************************")
        cmd = input("请输入您的骚操作选项:")
        if cmd.strip() == 'view list':
            ftp.do_list()
        elif cmd.strip()[:3] == "get":
            filename = cmd.strip().split(' ')[-1]
            ftp.do_get(filename)
        elif cmd.strip()[:3] == 'put':
            filename = cmd.strip().split(' ')[-1]
            ftp.do_put(filename)
        elif cmd.strip() == 'quit':
            ftp.do_quit()

# 网络连接

def main():
    ADDR = ('176.215.155.161',8888)
    sockfd = socket()
    try:
        sockfd.connect(ADDR)
    except Exception as e:
        print("连接服务器失败")
        return
    else:
        print('****************************************************')
        print('data                    file                   image')
        print('****************************************************')
        data = input("请输入文件种类")
        cls =data.strip()
        if cls not in ['data','file','image']:
            print("Sorry input Error")
            return
        else:
            sockfd.send(cls.encode())
            request(sockfd)# 发起具体请求

if __name__ == "__main__":
    main()