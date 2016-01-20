
"""
    repl module

    Uses the coreappliances repler to execute code but in a local manner.
"""

import sys
import os
import tempfile
import shutil
import subprocess
import time
import signal
import glob
from threading import Thread, Event

# Make sure we know where the core appliances are
APPLS = os.environ.get("EXIS_APPLIANCES", None)
if(APPLS is None):
    print("!" * 50)
    print("!! $EXIS_APPLIANCES not found, REPL may not work")
    print("!" * 50)

EXISREPO = os.environ.get("EXIS_REPO", None)
if(EXISREPO is None):
    print("!" * 50)
    print("!! $EXIS_REPO not found, REPL may not work")
    print("!" * 50)

ON_POSIX = "posix" in sys.builtin_module_names

SLEEP_TIME = 1

WS_URL = os.environ.get("WS_URL", "ws://localhost:8000/ws")
DOMAIN = os.environ.get("DOMAIN", "xs.demo.test")
BASEPATH = "{}/repler".format(APPLS)
TEST_PREFIX = "arbiterTask"


class Coder:

    """
    Super class that contains the methods needed for each language to deal with lang
    specific code and functions.
    """

    def __init__(self, task, action):
        self.task = task
        self.action = action

    def setup(self, tmpdir):
        print "!! Not implemented"
    
    def setupTerminate(self, code):
        print "!! Not implemented"

    def expect2assert(self):
        print "!! Not implemented"

    def checkExecution(self, out, err):
        """
        Take the stderr and stdout arrays and check if execute was ok or not.
        Also check the output for any expect data.
        Returns:
            String matching the output that led to the successful result,
            or None if a failure or no match
        """
        ev = self.getExpect()
        #print(ev, out, err)

        good = None
        # Sometimes we shouldn't expect anything and thats ok
        if ev is None:
            good = "no expect required"
        else:
            for o in out:
                if ev in o:
                    good = ev

        if err:
            # Look at the error to see whats up
            errOk = False
            for e in err:
                pass
            if not errOk:
                print "!! Found error:"
                print "\n".join(err)
                return None
        return good


class PythonCoder(Coder):
    def setup(self, tmpdir):
        """
        We shouldn't have to do anything here, assume they have run 'sudo pip install -e .' in pyRiffle.
        """
        pass

    def setupTerminate(self, code):
        """
        Assume the last line of the code is enough info to judge indenting
        Also assume they didn't use TABS!!!!!
        """
        if self.task.action in ("publish", "call"):
            c = self.task.code[-1]
            code.append("{}exit()".format(" " * (len(c) - len(c.lstrip(' ')))))

    def expect2assert(self):
        if self.task.expectLine >= 0:
            expectLine = self.task.code[self.task.expectLine]
            return expectLine.replace('print(', 'assert({} == '.format(self.task.expectVal))
        else:
            return None

    def getExpect(self):
        """
        Returns a properly formatted lang-specific value that we should be searching for.
        """
        if self.task.expectType == "str":
            return self.task.expectVal.strip("'\"")
        else:
            return self.task.expectVal

    def checkExecution(self, out, err):
        """
        Take the stderr and stdout arrays and check if execute was ok or not.
        Also check the output for any expect data.
        Returns:
            String matching the output that led to the successful result,
            or None if a failure or no match
        """
        ev = self.getExpect()
        #print(ev, out, err)

        good = None
        # Sometimes we shouldn't expect anything and thats ok
        if ev is None:
            good = "no expect required"
        else:
            for o in out:
                if ev in o:
                    good = ev

        if err:
            # Look at the error to see whats up
            errOk = False
            for e in err:
                # This needs to be fixed, its a gocore->python specific error that will go away!
                if "_shutdown" in e:
                    errOk = True
                    break
            if not errOk:
                print "!! Found error:"
                print "".join(err)
                return None
        return good


class SwiftCoder(Coder):
    def setup(self, tmpdir):
        """
        Need to copy over the proper files for swift build command (mantle/swiftRiffle).
        """
        # Copy Package from example
        swift = "{}/swift".format(EXISREPO)
        os.mkdir("{}/main".format(tmpdir))
        shutil.copy("{}/example/Package.swift".format(swift), "{}/main".format(tmpdir))
        shutil.copytree("{}/mantle".format(swift), "{}/mantle".format(tmpdir))
        os.mkdir("{}/swiftRiffle".format(tmpdir))
        shutil.copytree("{}/swiftRiffle/Riffle".format(swift), "{}/swiftRiffle/Riffle".format(tmpdir))
        if not os.path.exists("{}/swiftRiffle/Riffle/.git".format(tmpdir)):
            raise Exception("!! Please run 'make swift' so that swiftRiffle is git tagged properly")

    def setupTerminate(self, code):
        # TODO
        pass

    def expect2assert(self):
        # TODO
        return None

    def getExpect(self):
        """
        Returns a properly formatted lang-specific value that we should be searching for.
        """
        if self.task.expectType == "String":
            return self.task.expectVal.strip("'\"")
        else:
            return self.task.expectVal

class JSCoder(Coder):
    def setup(self, tmpdir):
        """
        Need to run 'npm install BASEPATH/js/jsRiffle' in the tmp dir.
        """
        #proc = subprocess.Popen(["npm", "install", "{}/js/jsRiffle/".format(EXISREPO)], cwd=tmpdir,
        proc = subprocess.Popen(["npm", "link", "jsriffle"], cwd=tmpdir,
                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, errors = proc.communicate()
        
        if proc.returncode:
            print "!! We expect that you have run 'sudo npm link' in the jsRiffle dir"
            raise Exception("Unable to setup for JS: {}".format(errors))

    def setupTerminate(self, code):
        # TODO
        pass

    def expect2assert(self):
        # TODO
        return None

    def getExpect(self):
        """
        Returns a properly formatted lang-specific value that we should be searching for.
        """
        if self.task.expectType == "String":
            return self.task.expectVal.strip("'\"")
        else:
            return self.task.expectVal


coders = {
    "py": PythonCoder,
    "swift": SwiftCoder,
    "js": JSCoder
}

def getCoder(task, action):
    """Returns an instance of the proper class or None"""
    c = coders.get(task.lang, None)
    return c(task, action) if c else None

class ReplIt:

    """
    This class holds onto all the components required to take a task and execute it.
    """

    def __init__(self, taskSet, action):
        self.action = action
        self.task = taskSet.getTask(action)
        if self.task is None:
            raise Exception("No Task found")
        self.lang = taskSet.getFullLang()
        self.proc = None
        self.stdout = list()
        self.stderr = list()
        self.readThd = None
        self.executing = False
        self.coder = None
        self.buildComplete = Event()
        self.runScript = None


    def setup(self):
        """
        Sets up a temp directory for this task and copies the proper code over (like a fake docker)
        """
        # Get the coder for this lang
        self.coder = getCoder(self.task, self.action)
        if not self.coder:
            raise Exception("Couldn't find the Coder for this lang")

        # Where is the repl code we need?
        if(self.lang == "js"):
            self.basepath = "{}/repl-nodejs".format(BASEPATH)
        else:
            self.basepath = "{}/repl-{}".format(BASEPATH, self.lang)

        # Find the run script, use run2 if it exists
        if os.path.exists("{}/run2.sh".format(self.basepath)):
            self.runScript = "run2.sh"
        elif os.path.exists("{}/run.sh".format(self.basepath)):
            self.runScript = "run.sh"
        else:
            print "!! Unable to find the run.sh command from EXIS_APPLIANCES"
            raise Exception()

        # Setup a temp dir for this test
        self.testDir = tempfile.mkdtemp(prefix=TEST_PREFIX)

        # Copy over everything into this new dir
        src = os.listdir(self.basepath + "/")
        for f in src:
            ff = os.path.join(self.basepath + "/", f)
            if(os.path.isfile(ff)):
                shutil.copy(ff, self.testDir)
            elif(os.path.isdir(ff)):
                shutil.copytree(ff, "{}/{}".format(self.testDir, f))

        # Now that the dir is setup, allow the coder to setup anything it needs for the lang
        self.coder.setup(self.testDir)
        
        # Setup env vars
        self.env = {
            "WS_URL": WS_URL,
            "DOMAIN": DOMAIN,
            "PATH": os.environ["PATH"]
        }

        # Language specific things
        self.env["PYTHONPATH"] = self.testDir

        # Get the code pulled and formatted
        self.execCode = self.getTestingCode()
        self.env["EXIS_REPL_CODE"] = self.execCode

    def _read(self, out, stor):
        """
        Threaded function that spins and reads the output from the executing process.
        """
        while(self.executing):
            for line in iter(out.readline, b''):
                if line.rstrip() == "___BUILDCOMPLETE___":
                    self.buildComplete.set()
                else:
                    stor.append(line.rstrip())
        out.close()

    def kill(self):
        """
        Kills the process and stops reading in the data from stdout.
        Returns:
            True if all ok, False otherwise
        """
        # print "KILL {} : {} @ {} PID {}".format(self.action, self.task.fullName(), self.testDir, self.proc.pid)
        self.executing = False
        # Need to bring out the big guns to stop the proc, this is because it launches separate children
        # so we first set the process group to a unique value (using preexec_fn below), then we kill that
        # unique process group with the command here:
        os.killpg(os.getpgid(self.proc.pid), signal.SIGTERM)
        # self.proc.kill()
        # self.proc.wait()

        res = self.coder.checkExecution(self.stdout, self.stderr)
        if res is not None:
            print "{} {} : SUCCESS (Found {})".format(self.action, self.task.fullName(), res)
            return True
        else:
            print "{} {} : FAILURE".format(self.action, self.task.fullName())
            print "Expected : '{}'".format(self.coder.getExpect())
            print "Stdout   : '{}'".format("\n".join(self.stdout))
            print "Stderr   : '{}'".format("\n".join(self.stderr))
            print "Code     : {}".format(self.task.fileName)
            print "Test dir : {}".format(self.testDir)
            print "Code Executed:"
            print self.execCode
            return False

    def cleanup(self):
        """
        Removes the temp dirs used for this test.
        """
        shutil.rmtree(self.testDir)

    def execute(self):
        """
        Launches the actual function. To do this properly we need to launch a reader
        thread for the stdout since this will result in a blocking call otherwise.
        This returns a threading.Event() which should be waited() on before starting the next
        ReplIt.execute function since there are race conditions between building of different langs.
        """
        self.executing = True
        print "EXEC {} : {} @ {}".format(self.action, self.task.fullName(), self.testDir)

        self.proc = subprocess.Popen(["./{}".format(self.runScript)], cwd=self.testDir, env=self.env,
                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=1,
                                     close_fds=ON_POSIX, preexec_fn=os.setsid)

        self.readOut = Thread(target=self._read, args=(self.proc.stdout, self.stdout))
        self.readOut.daemon = True

        self.readErr = Thread(target=self._read, args=(self.proc.stderr, self.stderr))
        self.readErr.daemon = True

        self.readOut.start()
        self.readErr.start()

    def getAssertedCode(self):
        """
        Returns the assert added code so that this code segment will not complete properly if
        the return type is not correct (because we replace the "print" with an "assert").
        """
        # TODO

    def getTestingCode(self):
        """
        This function returns the properly formatted code needed to make the repl calls work.
        This means two things: 1) On call/pub examples it adds the proper leave() at the end
        and 2) it replaces the # Expect code with the proper assert.
        """
        code = [a for a in self.task.code]
        self.coder.setupTerminate(code)

        return "\n".join(code)


def executeAll(taskList, actionList):
    """
    Given a list of tasks and an action it will zip them together and then execute them properly.
    """
    procs = list()
    for ts, a in zip(taskList, actionList):
        r = ReplIt(ts, a)
        r.setup()
        r.execute()
        a = r.buildComplete.wait(5)
        if a is False:
            print "!! {} never completed setup process (BUILDCOMPLETE never found)".format(ts)

        procs.append(r)

    # Now let the system do its thing
    time.sleep(SLEEP_TIME)

    # Go back through and terminate in reverse order
    ok = True
    for p in procs[::-1]:
        ok &= p.kill()

    # If everything was ok then cleanup the temp dirs
    if ok:
        for p in procs:
            p.cleanup()


def executeTaskSet(taskSet):
    """
    Given one specific TaskSet it will execute the corresponding components of that (pub/sub or reg/call).
    Returns:
        None if nothing happened
        True if it worked
        False if it didn't
    """
    procs = list()

    # Pull the proper actions from the task
    recv = taskSet.getTask("register") or taskSet.getTask("subscribe")
    send = taskSet.getTask("publish") or taskSet.getTask("call")

    if None in (recv, send):
        return None

    # Startup the actions
    for r in recv, send:
        rr = ReplIt(taskSet, r.action)
        rr.setup()
        rr.execute()
        a = rr.buildComplete.wait(5)
        if a is False:
            print "!! {} never completed setup process (BUILDCOMPLETE never found)".format(r)
        procs.append(rr)

    # Now let the system do its thing
    time.sleep(SLEEP_TIME)

    # Go back through and terminate in reverse order
    ok = True
    for p in procs[::-1]:
        ok &= p.kill()

    # If everything was ok then cleanup the temp dirs
    if ok:
        for p in procs:
            p.cleanup()
        return True
    else:
        return False


def cleanupTests():
    # NOTE: This only works on linux flavored systems right now
    dirs = glob.glob("/tmp/{}*".format(TEST_PREFIX))
    for d in dirs:
        print d
        shutil.rmtree(d)
