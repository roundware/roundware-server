# Roundware Server is released under the GNU Affero General Public License v3.
# See COPYRIGHT.txt, AUTHORS.txt, and LICENSE.txt in the project root directory.


class RoundException (Exception):

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message

    def __unicode__(self):
        return self.message
