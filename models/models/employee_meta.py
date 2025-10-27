from django.db import models

from models.models.meta import AcademicDegree, AcademicRank, Department, EmploymentForm, EmploymentStaff, StaffPosition, \
    EmployeeStatus, EmployeeType
from models.models.user import User

class EmployeeMeta(models.Model):
    meta_id = models.PositiveIntegerField(null=False, blank=False, unique=True)
    is_active = models.BooleanField(default=True, blank=False, null=False)
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='employee_meta',  # Bu qatorni qo'shing
        related_query_name='employee_meta',
    )
    academic_degree = models.ForeignKey(
        AcademicDegree,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="Academic darajasi"
    )
    academic_rank = models.ForeignKey(
        AcademicRank,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="Academic unvoni"
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="Kafedra / Bo'lim"
    )

    employment_form = models.ForeignKey(
        EmploymentForm,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="Mehnat shakli"
    )
    employment_staff = models.ForeignKey(
        EmploymentStaff,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="Stafkasi"
    )
    staff_position = models.ForeignKey(
        StaffPosition,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="Lavozim"
    )
    employee_status = models.ForeignKey(
        EmployeeStatus,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="Status"
    )
    employee_type = models.ForeignKey(
        EmployeeType,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="Xodim turi"
    )
    contract_number = models.CharField(
        max_length=100, blank=True, null=True,
        verbose_name="Kontrakt raqami"
    )
    decree_number = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="Buyruq raqami"
    )
    contract_date = models.DateField(null=True, blank=True,verbose_name="Kontrakt sanasi")
    decree_date = models.DateField(null=True, blank=True, verbose_name="Buyruq sanasi")

    hemis_created_at = models.DateTimeField(auto_now_add=True)
    hemis_updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

