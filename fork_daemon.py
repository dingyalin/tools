# -*-coding:utf-8-*-
import sys, os

'''将当前进程fork为一个守护进程

    注意：如果你的守护进程是由inetd启动的，不要这样做！inetd完成了
    所有需要做的事情，包括重定向标准文件描述符，需要做的事情只有
    chdir() 和 umask()了
'''
def daemonize(stdin='/dev/null',stdout= '/dev/null', stderr= 'dev/null'):
    '''Fork当前进程为守护进程，重定向标准文件描述符
        （默认情况下定向到/dev/null）
    '''
    #Perform first fork.
    try:
        pid = os.fork()
        if pid > 0:
            sys.exit(0)  #first parent out
    except OSError, e:
        sys.stderr.write("fork #1 failed: (%d) %s\n" %(e.errno, e.strerror))
        sys.exit(1)

    #从母体环境脱离
    os.chdir("/")
    os.umask(0)
    os.setsid()
    #执行第二次fork
    try:
        pid = os.fork()
        if pid > 0:
            sys.exit(0) #second parent out
    except OSError, e:
        sys.stderr.write("fork #2 failed: (%d) %s]n" %(e.errno,e.strerror))
        sys.exit(1)

    #进程已经是守护进程了，重定向标准文件描述符
    for f in sys.stdout, sys.stderr: f.flush()
    si = file(stdin, 'r')
    so = file(stdout,'a+')
    se = file(stderr,'a+',0)
    os.dup2(si.fileno(), sys.stdin.fileno())
    os.dup2(so.fileno(), sys.stdout.fileno())
    os.dup2(se.fileno(), sys.stderr.fileno())

def _example_main():
    '''示例函数：每秒打印一个数字和时间戳'''
    import time
    sys.stdout.write('Daemon started with pid %d\n' % os.getpid())
    sys.stdout.write('Daemon stdout output\n')
    sys.stderr.write('Daemon stderr output\n')

    c = 0
    while True:
        sys.stdout.write('%d: %s\n' %(c, time.ctime()))
        sys.stdout.flush()
        c = c+1
        time.sleep(1)

if __name__ == "__main__":
    daemonize('/dev/null','/home/hzhida/daemon.log','home/hzhida/daemon.log')
    _example_main()

#第一个fork是为了让shell返回，同时让你完成setsid（从你的控制终端移除，这样就不会意外地收到信号）。setsid使得这个进程成为“会话领导（session leader）”，即如果这个进程打开任何终端，该终端就会成为此进程的控制终端。我们不需要一个守护进程有任何控制终端，所以我们又fork一次。在第二次fork之后，此进程不再是一个“会话领导”，这样它就能打开任何文件（包括终端）且不会意外地再次获得一个控制终端

另外说明：
umask()函数为进程设置文件模式创建屏蔽字，并返回以前的值
在shell命令行输入：umask 就可知当前文件模式创建屏蔽字
常见的几种umask值是002，022和027，002阻止其他用户写你的文件，022阻止同组成员和其他用户写你的文件，027阻止同组成员写你的文件以及其他用户读写或执行你的文件
rwx-rwx-rwx  代表是777  所有的人都具有权限读写与执行

chmod()改变文件的权限位
int dup(int filedes) 返回新文件描述符一定是当前文件描述符中的最小数值
int dup2(int filedes, int filedes2);这两个函数返回的新文件描述符与参数filedes共享同一个文件表项。
