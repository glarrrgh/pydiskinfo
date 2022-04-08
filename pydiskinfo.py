"""A module for getting information about block devices in a system.

The pydiskinfo module is not a replacement for modules that gain file or 
filesystem information. It is mostly a supplement, for those rare situations 
when you need to know more about the physical devices rather than the 
filesystems and files on them. I made the module because I needed path 
information to do raw read off of hard drives. If other uses arise, I may be 
compelled to extend the module.

The module depends on the wmi module, when run on a windows system. No
extra modules need to be installed on linux systems. The linux functionality 
depends heavily on udev, so it will probably not work on other unix like 
systems. 

Copyright (c) 2022 Lars Henrik Ericson

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

from pydiskinfo_system import System


if __name__ == "__main__":
    import argparse
    argument_parser = argparse.ArgumentParser(description="List system block devices.")
    system = System()
    print(str(system))
