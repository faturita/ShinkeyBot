
import ConfigParser
import os
import io


def setconfig(configfile_name,option,value):
    with open(configfile_name) as f:
        sample_config = f.read()
    config = ConfigParser.RawConfigParser(allow_no_value=True)
    config.readfp(io.BytesIO(sample_config))

    cfgfile = open(configfile_name, 'w')
    config.set('server', option, value)
    config.write(cfgfile)
    cfgfile.close()

def readconfig(configfile_name):
    with open(configfile_name) as f:
        sample_config = f.read()
    config = ConfigParser.RawConfigParser(allow_no_value=True)
    config.readfp(io.BytesIO(sample_config))

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
        Config = ConfigParser.ConfigParser()
        Config.add_section('server')
        Config.set('server', 'ip', '10.17.66.164')
        Config.add_section('other')
        Config.set('other', 'use_anonymous', True)
        Config.write(cfgfile)
        cfgfile.close()
