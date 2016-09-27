from django.contrib.auth.models import User
from django.template import Template, Context
from django.test import TestCase
from django.conf import settings
from django.core.serializers import deserialize

from template_utils import functions

def render(src, ctx=None):
    return Template(src).render(Context(ctx))

class TemplateTest(TestCase):
    def setUp(self):
        self.test_user = User.objects.create(username='tester',email='test')
    
    def test_load(self):
        render("{% load func_tools comparison %}")
    
    def test_numeric(self):
        t = """{% if_less 1 2 %}y{% endif_less %}{% if_less_or_equal 1 2 %}y{% endif_less_or_equal %}{% if_greater 2 1 %}n{% endif_greater %}{% if_greater_or_equal 1 1 %}y{% endif_greater_or_equal %}"""
        self.assertEqual(render(t), 'yyny')
        
    def test_set_tag(self):
        t = "{% set src='import this' %}{{ src }}"
        self.assertEqual(render(t), 'import this')
        
    def test_del_tag(self):
        t = "{% del test %}{{ test }}"
        self.assertEqual(render(t,{'test': 'yup'}), '')

    def test_serialize(self):
        t = "{% serialize json users %}"
        json = render(t, {'users':User.objects.all()})
        self.assertEqual(deserialize('json', json).next().object.username, 'tester')
        
    def test_matches(self):
        t = "{% if_matches 'hiya' '\w{4}' %}yup{% endif_matches %}"
        self.assertEqual(render(t), 'yup')

    def test_contains(self):
        t = "{% if_contains 'team' 'i' %}yup{% endif_contains %}"
        self.assertEqual(render(t), '')
        
    def test_divisible_by(self):
        t = "{% if_divisible_by 150 5 %}buzz{% endif_divisible_by %}"
        self.assertEqual(render(t), 'buzz')

    def test_startswith(self):
        t = "{% if_startswith 'python' 'p' %}yup{% endif_startswith %}"
        self.assertEqual(render(t), 'yup')

    def test_subset(self):
        t = "{% if_subset l1 l2 %}yup{% endif_subset %}"
        self.assertEqual(render(t, {'l1':[2,3], 'l2':list(range(5))}), 'yup')

    def test_negate(self):
        t = "{% if_startswith 'python' 'p' negate %}yup{% endif_startswith %}"
        self.assertEqual(render(t), '')
        
    def test_negate_else(self):
        t = "{% if_startswith 'python' 'p' negate %}yup{% else %}nope{% endif_startswith %}"
        self.assertEqual(render(t), 'nope')

    def test_ctx_varname(self):
        t = "{% serialize json users as jsoncontent %}{{ jsoncontent|safe }}"
        json = render(t, {'users':User.objects.all()})
        self.assertEqual(deserialize('json', json).next().object.username, 'tester')
        
    def test_hassetting(self):
        t = "{% if_setting 'DEBUG' %}debug{% endif_setting %}"
        self.assertEqual(render(t), 'debug')

    def test_hash(self):
        ctx = {'foo':'bar'}
        
        sha1 = '62cdb7020ff920e5aa642c3d4066950dd1f01f4d'
        self.assertEqual(render('{{ foo|sha1 }}{% sha1 foo %}', ctx), sha1*2)

        md5 = '37b51d194a7513e45b56f6524f2d51f2'
        self.assertEqual(render('{{ foo|md5 }}{% md5 foo %}', ctx), md5*2)
        
    def test_greater(self):
        t = '{% if_greater 2 1 %}yup{% endif_greater %}'
        self.assertEqual(render(t), 'yup')
        
    def test_block(self):
        t = '{% render_var as myvar %}hallowtf{% endrender_var %}{{ myvar }}'
        self.assertEqual(render(t), 'hallowtf')
        
    # To test this next one:
    #   get markdown (pip install markdown)
    #   add 'django.contrib.markup'  to your INSTALLED_APPS
    #   set DEFAULT_BUILTIN_TAGS = ('django.contrib.markup' ,) in your settings
    if hasattr(settings, 'DEFAULT_BUILTIN_TAGS') and 'django.contrib.markup' in settings.INSTALLED_APPS:
        def test_defaults(self):
                t = "{{ src|markdown }}"
                self.assertEqual(render(t, {'src':'`i`'}), '<p><code>i</code></p>')