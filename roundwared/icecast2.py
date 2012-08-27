import libxml2
import urllib2
import os
import logging
import pycurl

class Admin:
        def __init__(self, host, username, password):
                self.__host = host
                auth_handler = urllib2.HTTPBasicAuthHandler()
                auth_handler.add_password('Icecast2 Server', self.__host, username, password)
                opener = urllib2.build_opener(auth_handler)
                urllib2.install_opener(opener)

        def get_mount_list (self):
		result = self.process_xml("/admin/listmounts", "//icestats/source/@mount")
		if result: return result
		else: return []

        def get_client_count (self, mount):
		result = self.process_xml(
			"/admin/listclients?mount=" + mount,
			"//icestats/source/Listeners")
		if result: return int(result[0])
		else: return 0

	def stream_exists (self, mount):
		for m in self.get_mount_list():
			if m == mount:
				return True
		return False

        def process_xml (self, url, xpath):
		doc = None
		try:
			resp = urllib2.urlopen("http://" + self.__host + url)
			respXML = resp.read()
			doc = libxml2.parseDoc(respXML)
			ctxt = doc.xpathNewContext()
			return map(lambda x: x.content, ctxt.xpathEval(xpath))
		except urllib2.HTTPError:
			return None
		finally:
			if(doc): doc.freeDoc()
			#FIXME: This was in the original code I used to learn this. Do I need it?
			#libxml2.dumpMemory()

	def update_metadata (self, asset_id, session_id):
		c = pycurl.Curl()
		c.setopt(pycurl.USERPWD, "admin:roundice")
		logging.debug("update metadata - enter")
		sysString = "http://" + self.__host +  "/admin/metadata.xsl?mount=/stream" + str(session_id) + ".mp3&mode=updinfo&charset=UTF-8&song=assetid" + str(asset_id) +""
		c.setopt(pycurl.URL, sysString)
		logging.debug("update metadata - sysString: "+ sysString)
		c.perform()
		logging.debug("update metadata - returning" )
		

		#r = os.system(sysString)
#        def getMetadata(self):
#                global basePath
#                command_url = self.__host + "/admin/stats.xml"
#                style_url = basePath + "/sbin/streamer/getMetadata.xsl"
#                dataList = self.processXML(command_url, style_url)
#                return dataList[0]


#        def moveMountPoints(self, src, dest):
#                command = "/admin/moveclients?mount=" + src + "&destination=" + dest
#                self.execCommand(command)


#        def execCommand(self, command):
#                try:
#                        resp = urllib2.urlopen("http://" + self.__host + command)
#                        print "exec: %s" % command
#                except:
#                        pass
#                        # print "Cannot move mountpoints %s" % command


