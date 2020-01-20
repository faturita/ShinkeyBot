
import configparser
import os
import io


def setconfig(configfile_name,option,value):
    config = configparser.RawConfigParser(allow_no_value=True)
    config.read(['config.ini'],encoding='cp1250')

    cfgfile = open(configfile_name, 'w')
    config.set('SERVER', option, value)
    config.write(cfgfile)
    cfgfile.close()

def readconfig(configfile_name):
    config = configparser.RawConfigParser(allow_no_value=True)
    config.read(['config.ini'],encoding='cp1250')

    #print("List all contents")
    for section in config.sections():
        #print("Section: %s" % section)
        for options in config.options(section):
            #print("x %s:::%s:::%s" % (options,
            #                  config.get(section, options),
            #                  str(type(options))))
            if (options == 'ip'):
                return config.get(section, options)

def createconfig(configfile_name):
    # Check if there is already a configurtion file
    if not os.path.isfile(configfile_name):
        # Create the configuration file as it doesn't exist yet
        cfgfile = open(configfile_name, 'w')

        # Add content to the file
        Config = configparser.ConfigParser()
        Config.add_section('SERVER')
        Config.set('SERVER', 'ip', '10.17.66.164')
        Config.write(cfgfile)
        cfgfile.close()
