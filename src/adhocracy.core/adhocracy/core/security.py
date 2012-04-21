SITE_ACL = [[u'Allow', u'system.Everyone', [u'view']],
            [u'Allow', u'role:viewer', [u'view']],
            [u'Allow', u'role:editor', [u'view', u'add', u'edit']],
            [u'Allow', u'role:owner', [u'view', u'add', u'edit', u'manage']],
           ]
