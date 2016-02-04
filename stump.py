#!/usr/bin/python

helpstr = '''Riffle maintenance and management.

Usage:
  stump init
  stump push (all | REPOS...)
  stump pull (all | REPOS...)
  stump add-subtree DIRECTORY NAME URL
  stump test (list | all | <languageOrTestNumber>)
  stump release <remote> <version>

Options:
  -h --help     Show this screen.


Testing Examples:
    ./stump test list       List all tests
    ./stump test all        Run all tests
    ./stump test python     Run all tests in language
    ./stump test 15         Run the given test number

Release Example:
    ./stump release pyRiffle 0.2.1
'''

import os
import sys
import docopt
from subprocess import call
import shutil
import tempfile
import arbiter

# Format: (prefix: remote, url)
SUBTREES = [
    ("ios/swiftRiffle", "swiftRiffle", "git@github.com:exis-io/swiftRiffle.git"),
    ("ios/appBackendSeed", "iosAppBackendSeed", "git@github.com:exis-io/iosAppBackendSeed.git"),
    ("ios/appSeed", "iosAppSeed", "git@github.com:exis-io/iosAppSeed.git"),
    ("ios/example", "iosExample", "git@github.com:exis-io/iOSExample.git"),

    ("js/jsRiffle", "jsRiffle", "git@github.com:exis-io/jsRiffle.git"),
    ("js/ngRiffle", "ngRiffle", "git@github.com:exis-io/ngRiffle.git"),
    ("js/angularSeed", "ngSeed", "git@github.com:exis-io/ngSeed.git"),

    ("core", "core", "git@github.com:exis-io/core.git"),

    ("python/pyRiffle", "pyRiffle", "git@github.com:exis-io/pyRiffle.git"),

    ("CardsAgainstHumanityDemo/swiftCardsAgainst", "iosCAH", "git@github.com:exis-io/CardsAgainst.git"),
    ("CardsAgainstHumanityDemo/ngCardsAgainst", "ngCAH", "git@github.com:exis-io/ionicCardsAgainstEXIStence.git")
]


if __name__ == '__main__':
    args = docopt.docopt(helpstr, options_first=True, help=True)
    allLanguages = ['swift', 'js', 'python']

    if args['init']:
        print "Adding remotes"

        for p, r, u in SUBTREES:
            call("git remote add %s %s" % (r, u,), shell=True)

        print "Linking go libraries"
        gopath = os.getenv('GOPATH', None)

        if gopath is None:
            print 'You dont have a $GOPATH set. Is go installed correctly?'
        else:
            corePath = os.path.join(gopath, 'src/github.com/exis-io/core')

            # Remove existing symlinks
            if os.path.islink(corePath):
                os.unlink(corePath)

            # Delete the library if there's anything there
            if os.path.exists(corePath):
                shutil.rmtree(corePath)

            os.symlink(os.path.abspath("core"), corePath)

    elif args['push']:
        if args['all']:
            repos = SUBTREES
        else:
            repos = [x for x in SUBTREES if x[1] in args['REPOS']]

        b = 'master'

        print "Pushing: ", repos

        for p, r, u in repos:
            call("git subtree push --prefix %s %s %s" % (p, r, b,), shell=True)

    elif args['pull']:
        repos = SUBTREES if args['all'] else args['REPOS']
        b = 'master'

        for p, r, u in repos:
            call("git subtree pull --prefix %s %s %s -m 'Update to stump' --squash" % (p, r, b,), shell=True)

    elif args['add-subtree']:
        call("git remote add %s %s" % (args['NAME'], args['URL'],), shell=True)
        call("git subtree add --prefix %s %s master" % (args['DIRECTORY'], args['NAME'],), shell=True)

        print 'Subtree added. Please edit the SUBTREES field in this script: \n("%s", "%s", "%s")' % (args['DIRECTORY'], args['NAME'], args['URL'])

    elif args['test']:
        os.environ["EXIS_REPO"] = os.getcwd()

        def orderedTasks(lang):
            '''
            Returns an orderd list of tasks from the arbiter 
            
            TODO:
                move the relative sorting down into the arbiter-- no need to repeat these steps all the time here
                Also jesus find another home for this method
            '''
            lang = None if lang == 'all' else lang
            tasks = [x for x in arbiter.arbiter.findTasks(shouldPrint=False, lang=lang)]
            tasks.sort(key=lambda x: x.index)

            return tasks

        # TODO: unit tests
        # TODO: integrate a little more tightly with unit and end to end tests

        # List the tests indexed in the order they were found 
        if args['list']:
            print " #\tTest Name"
            for task in orderedTasks(None):
                print " " + str(task.index) + "\t" + task.getName()

                #TODO: seperate by language
                #TODO: seperate by file, and use the files for some reasonable ordering

        elif args['all']: 
            arbiter.arbiter.testAll('all')

        elif args['<languageOrTestNumber>']:
            target = args['<languageOrTestNumber>']

            if target.isdigit():
                tasks = orderedTasks('all')
                target = next((x for x in tasks if x.index == int(target)), None)

                if target is None: 
                    print "Unable to find test #" + str(target)
                    sys.exit(0)

                arbiter.repl.executeTaskSet(target)
            else: 
                arbiter.arbiter.testAll(args['<languageOrTestNumber>'])

    elif args['release']:
        found = False
        for prefix, remote, url in SUBTREES:
            if remote == args['<remote>']:
                found = True
                break

        if not found:
            print("Error: unrecognized remote ({})".format(args['<remote>']))
            sys.exit(1)

        print("Pushing {} to remote {} ({})...".format(prefix, remote, url))
        call("git subtree push --prefix {} {} master".format(prefix, remote), shell=True)

        tag = args['<version>']
        if not tag.startswith("v"):
            tag = "v" + tag

        tmp = tempfile.mkdtemp()
        call("git clone {} {}".format(url, tmp), shell=True)

        print("Creating tag: {}".format(tag))
        call('git -C {0} tag -a {1} -m "Release {1}."'.format(tmp, tag), shell=True)
        call("git -C {} push origin master".format(tmp), shell=True)
        shutil.rmtree(tmp)




'''
Start xcode with open source swift version: 
    xcrun launch-with-toolchain /Library/Developer/Toolchains/swift-latest.xctoolchain

Use open source swift on command line: 
    export PATH=/Library/Developer/Toolchains/swift-latest.xctoolchain/usr/bin:"${PATH}"

Deployment scripts from old stump

ios() {
    echo "Updating riffle, seeds, and cards to version $1"

    git subtree push --prefix swift/swiftRiffle swiftRiffle master

    git clone git@github.com:exis-io/swiftRiffle.git
    cd swiftRiffle
    
    git tag $1 
    git push --tags

    pod trunk push --allow-warnings --verbose

    cd ..
    rm -rf swiftRiffle

    # update the seed projects and push them 
    cd swift/appSeed
    pod update

    cd ../appBackendSeed
    pod update
    cd ../..

    git add --all
    git commit -m "swRiffle upgrade to v $1"

    git subtree push --prefix swift/appBackendSeed iosAppBackendSeed master
    git subtree push --prefix swift/appSeed iosAppSeed master
    git push origin master
}

js() {
    echo "Updating js to version $1"

    browserify js/jsRiffle/index.js --standalone jsRiffle -o jsRiffle.js
    browserify js/jsRiffle/index.js --standalone jsRiffle | uglifyjs > jsRiffle.min.js

    mv jsRiffle.js js/jsRiffle/release/jsRiffle.js
    mv jsRiffle.min.js js/jsRiffle/release/jsRiffle.min.js

    cd js/jsRiffle
    npm version $1
    npm publish

    cd ../ngRiffle
    npm version $1
    npm publish

    cd ../..

    git add --all
    git commit -m "jsRiffle upgrade to v $1"

    git push origin master
    git subtree push --prefix js/jsRiffle jsRiffle master
    git subtree push --prefix js/ngRiffle ngRiffle master

    git clone git@github.com:exis-io/jsRiffle.git
    cd jsRiffle
    git tag $1 
    git push --tags
    cd ..
    rm -rf jsRiffle

    git clone git@github.com:exis-io/ngRiffle.git 
    cd ngRiffle
    git tag $1 
    git push --tags
    cd ..
    rm -rf ngRiffle

    # Do something with the seed app!
}
'''
