#!/usr/bin/python

#if 0 /*
# -----------------------------------------------------------------------
# wap_login.rpy - Wap interface login form.
# ----------------------------------------------------------------------- */
#endif

from wap_types import WapResource, FreevoWapResource

class WLoginResource(FreevoWapResource):

    def _render(self, request):

        fv = WapResource()
        form = request.args

        user = fv.formValue(form, 'user')
        passw = fv.formValue(form, 'passw')
        action = fv.formValue(form, 'action')
        
        fv.printHeader()

        fv.res += '  <card id="card1" title="Freevo Wap">\n'
        fv.res += '   <p><big><strong>Freevo Wap Login</strong></big></p>\n'

        if action <> "submit":

            fv.res += '       <p>User : <input name="user" title="User" size="15"/><br/>\n'
            fv.res += '          Passw : <input name="passw" type="password" title="Password" size="15"/></p>\n'
            fv.res += '   <do type="accept" label="Login">\n'
            fv.res += '     <go href="wap_rec.rpy" method="post">\n'
            fv.res += '       <postfield name="u" value="$user"/>\n'
            fv.res += '       <postfield name="p" value="$passw"/>\n'
            fv.res += '     </go>\n'
            fv.res += '   </do>\n'
            fv.res += '  </card>\n'

        fv.printFooter()

        return fv.res

resource = WLoginResource()
