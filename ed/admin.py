from django.contrib import admin

# Register your models here.
from .models import Institution
admin.site.register(Institution)
from .models import Branch
admin.site.register(Branch)
from .models import Course
admin.site.register(Course)
from .models import SupportingDoc
admin.site.register(SupportingDoc)
from .models import introBanner
admin.site.register(introBanner)
from .models import planBanner
admin.site.register(planBanner)
from .models import instituteBanner
admin.site.register(instituteBanner)
from .models import Staff
admin.site.register(Staff)
from .models import instituteBranch
admin.site.register(instituteBranch)
from .models import institutionCourse
admin.site.register(institutionCourse)
from .models import feeStructure
admin.site.register(feeStructure)
from .models import College,collegeBranch,collegeCourse,otherFeeStructure,courseType
admin.site.register(College)
admin.site.register(courseType)
admin.site.register(collegeBranch)
admin.site.register(collegeCourse)
admin.site.register(otherFeeStructure)