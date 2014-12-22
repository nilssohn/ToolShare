#!/usr/bin/env python
import os
import sys
#yo, look at this sick as code!
if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "toolshare.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
