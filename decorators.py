# Decorators
import getpass
import os

username = getpass.getuser()
print username
import sys
import subprocess
import rumps
import pexpect

# var = subprocess.check_output(["ssh -o 'BatchMode=yes' zahidmuh@hpcc.msu.edu 'echo 2>&1' && echo 'OK' || echo 'NOK' "],shell=True)


# p = subprocess.Popen(['open', '-a', 'Terminal', '-n'], stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.STDOUT)

# output = p.communicate(input = "ssh-keygen -t rsa")
#
# print(output)




#
# password = rumps.Window(secure=True).run()
#
#
# if not password.text:
#     print "No password entered"
# else:
#     print ("Password: {}".format(password.text))


cond = True


# while cond:
#     if 2 == 2 :
#         print "here"
#         break
#     else:
#         print "kobe"


def test():
    try:
        subprocess.check_call("pkgutil --pkg-info com.github.osxfuse.pkg.MacFUSE", shell=True)
        subprocess.check_call("pkgutil --pkg-info com.github.osxfuse.pkg.SSHFS", shell=True)
        return True
    except subprocess.CalledProcessError:
        return False
        # error_msg = rumps.alert(title="Software requirements",
        # message="You are missing somesoftware requirements. Please click on the link and install the necessary packages."


cur_usr = "/Users/" + "icer3" + "/.ssh"
print cur_usr
if ("id_rsa_hpcc" in os.listdir('/Users/icer3/.ssh')):
    print "It exists"


# try:
#     subprocess.check_call("pkgutil --pkg-info com.github.osxfuse.pkg.MacFUSE",shell=True)
#     subprocess.check_call("pkgutil --pkg-info com.github.osxfuse.pkg.SSHFS1", shell = True)
# except subprocess.CalledProcessError:
#     print "One of the programs dont exust"
#     alert = rumps.alert(title="SSH Keys",
#                             message="To mount your HPCC drive using SSHFS, you need to have SSH Key-Based "
#                                     "authentication. Would you like to continue to create your SSH Keys."
#
#
#
#                                     "For more Info",
#                             ok="Continue", cancel="Cancel")
#
#     if alert == 1 :
#         print("conTinued")
#     else:
#         print ("Canceled")
