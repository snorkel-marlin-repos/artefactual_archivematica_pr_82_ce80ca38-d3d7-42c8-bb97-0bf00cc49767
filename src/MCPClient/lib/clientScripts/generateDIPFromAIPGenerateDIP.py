#!/usr/bin/python -OO

# This file is part of Archivematica.
#
# Copyright 2010-2013 Artefactual Systems Inc. <http://artefactual.com>
#
# Archivematica is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Archivematica is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Archivematica.  If not, see <http://www.gnu.org/licenses/>.

# @package Archivematica
# @subpackage archivematicaClientScript
# @author Joseph Perry <joseph@artefactual.com>

import os
import sys
import shutil
sys.path.append("/usr/lib/archivematica/archivematicaCommon")
import databaseInterface
from databaseFunctions import createSIP

if __name__ == '__main__':
    #COPY THE METS FILE
    #Move the DIP Directory
    
    fauxUUID = sys.argv[1]
    unitPath = sys.argv[2]
    date = sys.argv[3]
    
    basename = os.path.basename(unitPath[:-1])
    uuidLen = 36
    originalSIPName = basename[:-(uuidLen+1)*2]
    originalSIPUUID = basename[:-(uuidLen+1)][-uuidLen:]
    METSPath = os.path.join(unitPath, "metadata/submissionDocumentation/data/", "METS.%s.xml" % (originalSIPUUID))
    if not os.path.isfile(METSPath):
        print >>sys.stderr, "Mets file not found: ", METSPath
        exit(-1)
    
    #move mets to DIP    
    src = METSPath
    dst = os.path.join(unitPath, "DIP", os.path.basename(METSPath))
    shutil.move(src, dst)
    
    #Move DIP
    src = os.path.join(unitPath, "DIP")
    dst = os.path.join("/var/archivematica/sharedDirectory/watchedDirectories/uploadDIP/", originalSIPName + "-" + originalSIPUUID)  
    shutil.move(src, dst)
    
    
    sql = """SELECT sipUUID from SIPs where sipUUID = '%s'; """ % (originalSIPUUID)
    rows = databaseInterface.queryAllSQL(sql)
    if not len(rows):
        #otherwise doesn't appear in dashboard
        import uuid
        createSIP(unitPath, UUID=originalSIPUUID)
        databaseInterface.runSQL("""INSERT INTO Jobs (jobUUID, jobType, directory, SIPUUID, currentStep, unitType, subJobOf, microserviceGroup) 
                 VALUES ('%s','Hack to make DIP Jobs appear', '%s', '%s', 'Completed successfully', 'unitSIP', '', 'Upload DIP');""" % (str(uuid.uuid4()), unitPath, originalSIPUUID))
        