#!/usr/bin/python
import os
import Console
#--------------------------------------------------------------------
os.environ['SDL_VIDEO_CENTERED'] = '1'
#--------------------------------------------------------------------
if __name__ == '__main__':
	con = Console.Console()
	con.start()
