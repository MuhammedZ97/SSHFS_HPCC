from urllib import urlretrieve
import os.path
import rumps
import subprocess
import os
import pipes
import glob
import pexpect
import getpass
import sys
import webbrowser
#import pip

class StatusBarApp(rumps.App):

    urlretrieve('http://www.mellanox.com/solutions/hpc/img/testimonials/icer.png', 'icer.png')

    def __init__(self):
        super(StatusBarApp, self).__init__("SSHFS") # refers to parent base class without explicitly calling their intits methods
        self.menu = [rumps.MenuItem('Mount HPCC',callback=self.mount,key='q'),rumps.MenuItem('Unmount',callback=self.unmount),
                    {
                        "More info":{"ICER","SSH KEYS"}
                    }
                    ]
        
        self.icon = 'icer.png'
        self.local_mount_point = "/Volumes"
        self.path = "/HPCC"
        self.login = getpass.getuser()
        rumps.debug_mode(True)

    def check_programs(self):
        check = os.system("pkgutil --pkgs | grep 'FUSE'")
        check1 = os.system("pkgutil --pkgs | grep 'SSHFS'")
        if (check == 0 and check1 == 0):
            return True

    #def install_module(self,package):
        #pip.main(['install',package])

    def key_present(self,userid):
        # Batchmode=yes and password less connectivity is enable the command execute successfully on remote, else it will return error and continues.
        var = subprocess.check_output(
            ["ssh -o 'BatchMode=yes' " + userid + "@hpcc.msu.edu 'echo 2>&1' && echo 'OK' || echo 'NOK' "], shell=True)
        if var.strip() == "OK":
            return True
        return False

    def gen_key(self):
        #home = os.path.expanduser('~')
        if (os.path.isfile("~/Users/icer3/.ssh/id_rsa_hpcc") == False):
            self.ssh_passphrase = rumps.Window(title="RSA private key passphrase",message="Enter passphrase (empty for no passphrase:)",secure=True,dimensions=(250,50)).run()
            if not self.ssh_passphrase.text:
                subprocess.call("ssh-keygen -t rsa -f  ~/.ssh/id_rsa_hpcc", shell=True)     # changed this to hpcc
            else:
                subprocess.call("ssh-keygen -t rsa -N " + self.ssh_passphrase.text + " -f ~/.ssh/id_rsa_hpcc", shell=True)      # changed this to hpcc
            # ssh - keygen - t rsa - q - f "$HOME/.ssh/id_rsa" - N""
        else:
            print ("No File is present")

    def exists_remote(self, userid):
        """Test if a file exists at path on a host accessible with SSH."""
        status = subprocess.call(
            ['ssh', userid + '@hpcc.msu.edu', 'test -f {}'.format(pipes.quote('.ssh/id'))])
        if status == 0:
            return True
        if status == 1:
            return False
        raise Exception('SSH failed')

    def push_key(self, userid):
        path = os.chdir("/Users/" + self.login + "/.ssh")
        Files = glob.glob1(path, '*.pub')
        public_id = Files[0]
        print (public_id)
        child = pexpect.spawn("scp -o StrictHostKeyChecking=no " + "/Users/" + self.login + "/.ssh/" + public_id + " " + userid + "@hpcc.msu.edu:.ssh/authorized_keys")
        #print '/bin/cat ~/.ssh/id_rsa.pub | ssh ' + userid + '@hpcc.msu.edu -o StrictHostKeyChecking=no "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys"'
        #child = pexpect.spawn("cat ~/.ssh/id_rsa.pub | ssh " + userid + "@hpcc.msu.edu -o StrictHostKeyChecking=no 'cat >> ~/.ssh/authorized_keys'")
        child.expect('Password:')
        #child.expect(pexpect.EOF, timeout=None)
        #print child.expect(pexpect.EOF)
        self.HPCC_PASS = rumps.Window(title="HPCC Password",message="Please enter your HPCC password:",dimensions=(250,50),secure=True).run()
        mypassword = str(self.HPCC_PASS.text)
        child.sendline(mypassword)

        Max_attempts = 3
        Attempt = 1
        while True:
            result = child.expect(['Password:', pexpect.EOF, pexpect.TIMEOUT])
            print (result, "result")
            if result == 0 and Max_attempts >= 1:
                self.HPCC_PASS = rumps.Window(title="Incorrect HPCC password.   Attempt: (""/3)", message="Please re-enter your HPCC password:",
                                          dimensions=(250, 50), secure=True).run()
                mypassword = str(self.HPCC_PASS.text)
                child.sendline(mypassword)
            elif Max_attempts < 1:
                self.message = rumps.alert(title="Incorrect HPCC password and userID",message="Please check your that you entered your HPCC username or Password Correctly.")
                sys.exit(0)
            else:
                break
            Max_attempts -= 1

        del mypassword

    def drive_mounted(self):
        return (os.path.exists(self.local_mount_point + self.path))

    @rumps.clicked("Mount HPCC")
    def mount(self, _):

        if ( not self.check_programs()):
            self.rumps.Window(title="Missing Requirements", message ="Need to install MacFUSE and SSHFS. Link: https://osxfuse.github.io")
            self.exit()

        #if (os.system("pip freeze | grep 'pexpect'")) != 0:  # if it does not == 0 it is not installed so then call pip install function
        #  self.install_module("pexpect")

        print(self.login)

        self.UID = rumps.Window(title="HPCC username",message="Please enter your MSU NETID:", dimensions=(250, 50)).run()

        UserID = str(self.UID.text)  # since rumps.Window returns its type from window class we need to convert it to string

        if (self.key_present(UserID)): # SSH does not connect through
            print ("The SSH keys are present {}".format(self.key_present(UserID)))
        else:
            print ("Need to generate ssh keys")

            self.alert = rumps.alert(title="SSH Keys",
                                     message="To mount your HPCC drive using SSHFS, you need to generate SSH Key-Based "
                                             "authentication. Would you like to continue to create your SSH Keys. NOTE: "
                                             "By clicking continue, the program will generate two files onto your computer "
                                             "system, a public and a private key. Additionally, the public key will be copied "
                                             "to your HPCC system account to a file within the your home directory at ~/.ssh/authorized_keys."
                                             " This procedure will enable Password-less login when connecting to the HPCC. This way, you'll "
                                             "be able to automatically login each time immediately without needing to enter your password. ",
                                     ok="Continue", cancel="Cancel")

            if self.alert == 0:
                    sys.exit()
            self.gen_key()
            self.push_key(UserID)

        sshfs_cmd = "/usr/local/bin/sshfs -o allow_other,defer_permissions,IdentityFile=~/.ssh/id_rsa_hpcc"
        remote_host = "@hpcc.msu.edu:/mnt/home/"
        options = "-o cache=no -o nolocalcaches -o volname=hpcc -o StrictHostKeyChecking=no"
        # StrictHostKeyChecking ignores authentication for first time use

        os.mkdir(self.local_mount_point + self.path)
        var = sshfs_cmd + " " + UserID + remote_host + UserID +  " " + self.local_mount_point + self.path + " " + options

        print(var)
        os.system(var)
        if (self.drive_mounted()):     # os.system() returns the encoded process exit value. 0 means succecss no error
             self.menu["Mount HPCC"].set_callback(None)
             rumps.notification(title="HPCC drive Mounted", subtitle="Sucessfull",  # !!!!Fix This
                               message="Your drive is located at " + self.local_mount_point + self.path,sound=True)

    @rumps.clicked("Unmount")
    def unmount(self, _):
        if (self.drive_mounted()):
            subprocess.call("diskutil umount" + " " +  self.local_mount_point + self.path, shell = True)
            self.menu["Mount HPCC"].set_callback(self.mount)
        else:
            self.alert = rumps.alert(title = "HPCC drive not currently mounted",message="Your HPCC drive is not mounted")

    @rumps.clicked("More info")
    def more_info(self,_):
        rumps.MenuItem("More Info")
        b = webbrowser.get('safari')
        b.open("https://icer.msu.edu")


if __name__ == "__main__":
    StatusBarApp().run()
