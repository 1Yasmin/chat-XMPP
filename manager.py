#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import logging
import getpass
from optparse import OptionParser

import sleekxmpp
from sleekxmpp.exceptions import IqError, IqTimeout
from sleekxmpp import ClientXMPP
import ssl


# Python versions before 3.0 do not use UTF-8 encoding
# by default. To ensure that Unicode is handled properly
# throughout SleekXMPP, we will set the default encoding
# ourselves to UTF-8.
if sys.version_info < (3, 0):
    from sleekxmpp.util.misc_ops import setdefaultencoding
    setdefaultencoding('utf8')
else:
    raw_input = input


class RegisterBot(sleekxmpp.ClientXMPP):

    def __init__(self, jid, password):
        sleekxmpp.ClientXMPP.__init__(self, jid, password)
        self.add_event_handler("session_start", self.start, threaded=True)
        self.add_event_handler("register", self.register, threaded=True)
        
        # Setup the plugins.
        self.register_plugin('xep_0030') # Service Discovery
        self.register_plugin('xep_0004') # Data forms
        self.register_plugin('xep_0066') # Out-of-band Data
        self.register_plugin('xep_0077') # In-band Registration
        
        # Some servers don't advertise support for inband registration, even
        # though they allow it. If this applies to your server, use:
        self['xep_0077'].force_registration = True
        
        # Adjust the SSL version used:
        self.ssl_version = ssl.PROTOCOL_TLS

    def start(self, event):
        self.send_presence()
        self.get_roster()

        # We're only concerned about registering, so nothing more to do here.
        self.disconnect()

    def register(self, iq):
        resp = self.Iq()
        resp['type'] = 'set'
        resp['register']['username'] = self.boundjid.user
        resp['register']['password'] = self.password

        try:
            resp.send(now=True)
            logging.info("Account created for %s!" % self.boundjid)
        except IqError as e:
            logging.error("Could not register account: %s" %
                    e.iq['error']['text'])
            self.disconnect()
        except IqTimeout:
            logging.error("No response from server.")
            self.disconnect()

class SessionBot(sleekxmpp.ClientXMPP):

    def __init__(self, jid, password):
        sleekxmpp.ClientXMPP.__init__(self, jid, password)

        # events 
        self.add_event_handler("session_start", self.start, threaded=True)
        self.add_event_handler("message", self.message, threaded = True)
        
        # Setup the plugins.
        self.register_plugin('xep_0030') # Service Discovery
        self.register_plugin('xep_0004') # Data forms
        self.register_plugin('xep_0066') # Out-of-band Data
        self.register_plugin('xep_0077') # In-band Registration
        self.register_plugin('xep_0030') # Service Discovery
        self.register_plugin('xep_0199') # XMPP Ping

        # Adjust the SSL version used:
        self.ssl_version = ssl.PROTOCOL_TLS

    def start(self, event):
        self.send_presence()

        try:
            self.get_roster()
        except IqError as err:
             logging.error('There was an error getting the roster')
             logging.error(err.iq['error']['condition'])
             self.disconnect()
        except IqTimeout:
             logging.error('Server is taking too long to respond')
             self.disconnect()
        

    def message(self, msg):
        if msg['type'] in ('chat', 'normal'):
            print("Message\n%(body)s" % msg)
            
    def removeAccount(self):
        resp = self.Iq()
        resp['type'] = 'set'
        resp['from'] = self.boundjid
        resp['register'] = ' '
        resp['register']['remove'] = ' '
        
        try:
            print(resp)
            resp.send(now=True)
        except IqError as e:
            logging.error("Could not delete account: %s" %
                    e.iq['error']['text'])
            self.disconnect()
        except IqTimeout:
            logging.error("No response from server.")
            self.disconnect()


if __name__ == '__main__':
    # Setup the command line arguments.
    optp = OptionParser()

    # Output verbosity options.
    optp.add_option('-q', '--quiet', help='set logging to ERROR',
                    action='store_const', dest='loglevel',
                    const=logging.ERROR, default=logging.INFO)
    optp.add_option('-d', '--debug', help='set logging to DEBUG',
                    action='store_const', dest='loglevel',
                    const=logging.DEBUG, default=logging.INFO)
    optp.add_option('-v', '--verbose', help='set logging to COMM',
                    action='store_const', dest='loglevel',
                    const=5, default=logging.INFO)

    # JID and password options.
    optp.add_option("-j", "--jid", dest="jid",
                    help="JID to use")
    optp.add_option("-p", "--password", dest="password",
                    help="password to use")

    opts, args = optp.parse_args()

    # Setup logging.
    logging.basicConfig(level=opts.loglevel,
                        format='%(levelname)-8s %(message)s')

    op_inicial = input(" 1.Register \n 2.Iniciar sesión \n Intruzca el numero de su opción: ")
    
    # Set values of username and password
    if opts.jid is None:
        opts.jid = raw_input("Username: ")
    if opts.password is None:
        opts.password = getpass.getpass("Password: ")
    
    # Make register
    if (op_inicial == "1"):
        xmp = RegisterBot(opts.jid, opts.password)
    
    #Make login
    elif (op_inicial == "2"):
        xmpp = SessionBot(opts.jid, opts.password)
        connect = True
    # Exit if the option does not exist
    else:
        sys.exit()

    
    start = False
    # login after make register
    if (op_inicial == "1"):
        # Connect to the XMPP server and start process5ing XMPP stanzas.
        if xmp.connect(('alumchat.xyz', 5222)):
            xmp.process(block=False)
            op = input("Desea iniciar sesión? (s/n):  ")
            if (op == "s"):
                print("s")
                op_inicial = "2"
                start = True
            elif (op == "n"):
                sys.exit()
                
    # Process for the active session
    if (op_inicial == "2"):
        #Only if the user comes from the register
        if (start == True):
            connect = True
            xmpp = SessionBot(opts.jid, opts.password)
        
        if xmpp.connect(('alumchat.xyz', 5222)):
            xmpp.process(block=False)
            print("Inicio de sesión realizado")
            
            # Options of the session
            while connect == True:
                # Menu
                act = input(" 1. Mostrar contactos y su estado \n 2. Agregar usuario a los contactos\n"+ 
                            " 3. Detalles de un contacto \n 4. Mensaje a un contacto \n" +
                            " 5. Chat grupal \n 6. Mensaje de presencia \n 7. Enviar archivo \n" +
                            " 8. Cerrar sesión \n 9. Eliminar cuenta \n Escriba el numero de la opción: ")
                        
                #Actions 
                # Show contacts and state
                if(act == "1"):
                    print(xmpp.client_roster)
                # Add user
                if(act == "2"):
                    contact = input("Contacto que desea añadir: ")
                    xmpp.send_presence()
                    xmpp.send_presence(pto=contact, ptype='subscribe')
                                         
                # Contact details
                if(act == "3"):
                    pass
                            
                # Private message
                if(act == "4"):
                    dest = input("Cuenta destino: ")
                    msg = input("mensaje: ")
                    xmpp.send_message(mto=dest, mbody=msg, mtype='chat')
                        
                #Group chat
                if(act == "5"):
                    pass
                            
                #Presence message
                if(act == "6"):
                    pass
                            
                # Send a file
                if(act == "7"):
                    pass
                        
                # Sign out
                if(act == "8"):
                    print("Hasta pronto!")
                    xmpp.disconnect()
                    break
                            
                #Delete account
                if(act == "9"):
                    xmpp.removeAccount()
                    xmpp.disconnect()
                    ("Bye! ")
