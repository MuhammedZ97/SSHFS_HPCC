from urllib import urlretrieve
import rumps
import subprocess
import os
import pipes
import glob
import pexpect
import getpass

class StatusBarApp(rumps.App):

    urlretrieve('http://www.mellanox.com/solutions/hpc/img/testimonials/icer.png', 'icer.png')

    def __init__(self):
        super(StatusBarApp, self).__init__("SSHFS") # refers to parent base class without explicitly calling their intits methods
        self.menu = [rumps.MenuItem('Mount HPCC',callback=self.mount,key='q'),rumps.MenuItem('Add Host',key='a'),rumps.MenuItem('Unmount',callback=self.unmount)]
        self.icon = 'icer.png'
        self.local_mount_point = "/Volumes"
        self.path = "/HPCC"
        self.login = getpass.getuser()
        rumps.debug_mode(True)          # Turn on debugging mode while editiing

    def key_present(self):              # checks to see if file
        CUR_USR = "/Users/" + self.login + "/.ssh"
        return ("id_rsa" in os.listdir(CUR_USR))

    def gen_key(self):                  # generate the keys
        home = os.path.expanduser('~')
        subprocess.call('ssh-keygen -t rsa -q -f ' + home + '/.ssh/id_rsa ', shell=True)
        # ssh - keygen - t rsa - q - f "$HOME/.ssh/id_rsa" - N""

    def exists_remote(self, userid):
        """Test if a file exists at path on a host accessible with SSH."""
        status = subprocess.call(
            ['ssh', userid + '@hpcc.msu.edu', 'test -f {}'.format(pipes.quote('.ssh/id'))])
        if status == 0:
            return True
        if status == 1:
            return False
        raise Exception('SSH failed')

    def push_key(self, userid): # copy over to the ssh
        path = os.chdir("/Users/" + self.login + "/.ssh")
        Files = glob.glob1(path, '*.pub')
        public_id = Files[0]
        child = pexpect.spawn('scp -o StrictHostKeyChecking=no ' + "/Users/" + self.login + "/.ssh/" + public_id + " " + userid + "@hpcc.msu.edu:.ssh/authorized_keys")
        child.expect_exact('Password:')
        self.Window = rumps.Window("Please enter your HPCC password:",dimensions=(150,50)).run()
        mypassword = str(self.Window.text)
        child.sendline(mypassword)
        child.expect(pexpect.EOF, timeout=None)

    def drive_mounted(self):
        return (os.path.exists(self.local_mount_point + self.path))

    @rumps.clicked("Mount HPCC")
    def mount(self, _):

        print(self.login)

        self.Window = rumps.Window("Please enter your MSU NETID", dimensions=(250, 50)).run()  # Holds information from user interaction with a rumps after it has been closed

        UserID = str(self.Window.text)  # since rumps.Window returns its type from window class we need to convert it to string

        if (self.key_present()):
            print ("The SSH keys are present {}".format(self.key_present()))
        else:
            print "Need to generate ssh keys"
            self.alert = rumps.alert(message="To mount your HPCC drive using SSHFS, you need to have SSH Key-Based authentication. Would you like to"
                                             "continue to create your SSH Keys. ")
            self.gen_key()
            self.push_key(UserID)

        #bool = self.exists_remote(UserID)
        #if(bool):
        #   print("Authorized_keys exist")

        #os.chdir("/Users/" + self.login + "/.ssh")
        #cwd = os.getcwd()

        sshfs_cmd = "/usr/local/bin/sshfs -o allow_other,defer_permissions,IdentityFile=~/.ssh/id_rsa"
        remote_host = "@rsync.hpcc.msu.edu:/mnt/home/"
        options = "-o cache=no -o nolocalcaches -o volname=hpcc -o StrictHostKeyChecking=no"   # StrictHostKeyChecking ignores authentication for first time use

        os.mkdir(self.local_mount_point + self.path)
        var = sshfs_cmd + " " + UserID + remote_host + UserID +  " " + self.local_mount_point + self.path + " " + options

        print(var)
        os.system(var)

        if (self.drive_mounted()):                                                    # os.system() returns the encoded process exit value. 0 means succecss no error
             self.menu["Mount HPCC"].set_callback(None)
             rumps.notification(title="HPCC drive Mounted 1", subtitle="Sucessfull",  # !!!!Fix This
                               message="Your drive is located at " + self.local_mount_point+self.path)

    @rumps.clicked("Unmount")
    def unmount(self, _):
        if (self.drive_mounted()):
            subprocess.call("diskutil umount" + " " +  self.local_mount_point + self.path, shell = True)
            self.menu["Mount HPCC"].set_callback(self.mount)
        else:
            self.alert = rumps.alert(message="Your HPCC drive is not mounted")


    @rumps.clicked("Add Host")
    def add_host(self, _):
        pass

if __name__ == "__main__":
    StatusBarApp().run()
