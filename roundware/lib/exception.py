# Roundware Server is released under the GNU Lesser General Public License.
# See COPYRIGHT.txt, AUTHORS.txt, and LICENSE.txt in the project root directory.

class RoundException (Exception):

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)
