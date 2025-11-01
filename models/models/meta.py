from django.db import models

# Talaba holati
class StudentStatus(models.Model):
    name = models.CharField(verbose_name="Talim shakli: ", max_length=250, null=True, blank=True)
    code = models.CharField(verbose_name="Talim shakli kodi: ", unique=True, max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Student status - Student holati"
        ordering = ['-created_at']

    def __str__(self):
        return self.name




class EducationForm(models.Model):
    name = models.CharField(verbose_name="Talim shakli: ", max_length=250, null=True, blank=True)
    code = models.CharField(verbose_name="Talim shakli kodi: ", unique=True, max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Education form - Ta'lim shakli"
        ordering = ['-created_at']

    def __str__(self):
        return self.name




class EducationType(models.Model):
    name = models.CharField(verbose_name="Talim turi: ", max_length=250, null=True, blank=True)
    code = models.CharField(verbose_name="Talim turi kodi: ", unique=True, max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Education type - Ta'lim turi"
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    @property
    def survey_question_count(self):
        from models.models.survey import SurveyQuestion
        return SurveyQuestion.objects.filter(survey__education_type_id=self.id).count()

    @property
    def student_count(self):
        from models.models.student_meta import StudentMeta
        return StudentMeta.objects.filter(education_type__id=self.id).count()


class EducationLang(models.Model):
    name = models.CharField(verbose_name="Kafedra nomi: ", max_length=250, null=True, blank=True)
    code = models.CharField(verbose_name="Kafedra kodi: ", max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Education lang - Ta'lim tili"
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class PaymentForm(models.Model):
    name = models.CharField(max_length=250, null=True, blank=True)
    code = models.CharField(unique=True, max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Payment form - To'lov formasi"
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class StudentType(models.Model):
    name = models.CharField(verbose_name="Talim shakli: ", max_length=250, null=True, blank=True)
    code = models.CharField(verbose_name="Talim shakli kodi: ", unique=True, max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Student type - Student turi"
        ordering = ['-created_at']

    def __str__(self):
        return self.name




class StructureType(models.Model):
    name = models.CharField(max_length=250, null=True, blank=True)
    code = models.CharField(unique=True, max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Structure Type"
        ordering = ['-created_at']

    def __str__(self):
        return self.name



class Department(models.Model):
    hemis_id = models.IntegerField(unique=True, verbose_name="Department ID", null=True, blank=True)
    code = models.CharField(unique=True, verbose_name="Kafedra kodi: ", max_length=100, null=True, blank=True)
    name = models.CharField(verbose_name="Kafedra nomi: ", max_length=250, null=True, blank=True)
    structureType = models.ForeignKey(
        StructureType,
        verbose_name="Struktura",
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    parent = models.ForeignKey(
        'self',
        verbose_name="Department parent",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='child_departments'
    )
    is_active = models.BooleanField(default=True, null=False, blank=False, verbose_name="activligi")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Department - Departmentlar ro'yxati"
        ordering = ['-created_at']

    def __str__(self):
        return self.name




class Specialty(models.Model):
    hemis_id = models.IntegerField(verbose_name="Specialty - Hemis yunalish",unique=True, null=True, blank=True)
    code = models.CharField(verbose_name="Yo'nalish kodi: ", max_length=100, null=True, blank=True)
    name = models.CharField(verbose_name="Yo'nalish nomi: ", max_length=250, null=True, blank=True)
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        verbose_name="Fakultet: ",
        null=True,
        blank=True
    )
    education_type = models.ForeignKey(
        EducationType,
        verbose_name="Ta'lim turi: ",
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    is_active = models.BooleanField(default=True, null=False, blank=False, verbose_name="activligi")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Specialty - Yo'nalishlar"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.code} - {self.name}"




class Group(models.Model):
    hemis_id = models.IntegerField(unique=True, verbose_name="Hemis id", null=True, blank=True)
    code = models.CharField(unique=True, verbose_name="Kafedra kodi: ", max_length=100, null=True, blank=True)
    name = models.CharField(verbose_name="Kafedra nomi: ", max_length=250, null=True, blank=True)
    department = models.ForeignKey(
        Department,
        verbose_name="group",
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    specialty = models.ForeignKey(
        Specialty,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='group'
    )
    education_Lang = models.ForeignKey(
        EducationLang,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='group'
    )
    is_active = models.BooleanField(verbose_name="Is active?", default=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Group - Guruhlar"
        ordering = ['-created_at']





class StudentLevel(models.Model):
    name = models.CharField(verbose_name="Nomi: ", max_length=250, null=True, blank=True)
    code = models.CharField(verbose_name="codi: ", unique=True, max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "StudentLevel - Student leveli"
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class SocialCategory(models.Model):
    code = models.CharField(verbose_name="Ijtimoiy holati kodi: ", unique=True, max_length=100, null=True, blank=True)
    name = models.CharField(verbose_name="Ijtimoiy holati: ", max_length=250, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "SocialCategory - Ijtimoiy holati"
        ordering = ['-created_at']

    def __str__(self):
        return self.name



class AcademicDegree(models.Model):
    name = models.CharField(verbose_name="Nomi ", max_length=250, null=True, blank=True)
    code = models.CharField(verbose_name="Codi ", unique=True, max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Academic Degree - Akademik daraja"
        ordering = ['-created_at']

    def __str__(self):
        return self.name

class AcademicRank(models.Model):
    name = models.CharField(verbose_name="Nomi ", max_length=250, null=True, blank=True)
    code = models.CharField(verbose_name="Codi ", unique=True, max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    class Meta:
        verbose_name_plural = "Academic Rank - Akademik unvoni"
        ordering = ['-created_at']




class EmploymentForm(models.Model):
    code = models.CharField(max_length=100, null=False, blank=False, unique=True)
    name = models.CharField(max_length=255, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "EmploymentForm - Xodimlar mehnat shakillari"
        ordering = ['-created_at']


    def __str__(self):
        return self.name




class EmploymentStaff(models.Model):
    code = models.CharField(max_length=100, null=False, blank=False, unique=True)
    name = models.CharField(max_length=255, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "EmploymentStaff - Xodimlar ish stavkalari"
        ordering = ['-created_at']

    def __str__(self):
        return self.name



class StaffPosition(models.Model):
    code = models.CharField(verbose_name="Codi ", unique=True, max_length=100, null=True, blank=True)
    name = models.CharField(verbose_name="Nomi ", max_length=250, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "StaffPosition - Hodim lavozimi"
        ordering = ['-created_at']

    def __str__(self):
        return self.name




class EmployeeStatus(models.Model):
    code = models.CharField(max_length=100, null=False, blank=False, unique=True)
    name = models.CharField(max_length=255, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "EmployeeStatus - Xodimlar xolati"
        ordering = ['-created_at']

    def __str__(self):
        return self.name



class EmployeeType(models.Model):
    code = models.CharField(max_length=100, null=False, blank=False, unique=True)
    name = models.CharField(max_length=255, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "EmployeeType - Xodim turi"
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class Subject(models.Model):
    hemis_id = models.IntegerField(db_index=True, unique=True, verbose_name="Hemis id: ", null=True, blank=True)
    name = models.CharField(verbose_name="Nomi: ", max_length=250, null=True, blank=True)
    code = models.CharField(verbose_name="kodi: ", max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Subject - Fanlar"
        ordering = ['-created_at']

    def __str__(self):
        return self.name




class Semester(models.Model):
    code = models.CharField(verbose_name="kodi: ", max_length=100, null=True, blank=True, unique=True)
    name = models.CharField(verbose_name="nomi: ", max_length=250, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Semester"
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class EducationYear(models.Model):
    name = models.CharField(verbose_name="Talim yili: ", max_length=250, null=True, blank=True)
    code = models.CharField(verbose_name="Talim yili kodi: ", max_length=100,unique=True, null=True, blank=True)
    current = models.BooleanField(verbose_name="Aktiv yil: ", null=True, blank=True, default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "EducationYear - Ta'lim yili"
        ordering = ['-created_at']

    def __str__(self):
        return self.name



class TrainingType(models.Model):
    name = models.CharField(verbose_name="Mashg'ulot turi: ", max_length=250, null=True, blank=True)
    code = models.CharField(verbose_name="Mashg'ulot kodi: ", max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "TrainingType - Dars turi"
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class LessonPair(models.Model):
    name = models.CharField(verbose_name="Nomi: ", max_length=250, null=True, blank=True)
    code = models.CharField(verbose_name="Kodi: ", max_length=100, null=True, blank=True)
    start_time = models.CharField(verbose_name="Boshlanish vaqti: ", max_length=5, null=True, blank=True)
    end_time = models.CharField(verbose_name="Tugash vaqti: ", max_length=5, null=True, blank=True)
    education_year = models.ForeignKey(EducationYear, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "LessonPair - Dars vaqtlari"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.id} - {self.start_time} - {self.end_time}"


class AuditoriumType(models.Model):
    name = models.CharField(verbose_name="Nomi: ", max_length=250, null=True, blank=True)
    code = models.CharField(verbose_name="Kodi: ", max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Building(models.Model):
    name = models.CharField(verbose_name="Nomi: ", max_length=250, null=True, blank=True)
    hemis_id = models.IntegerField(null=True, blank=True, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Auditorium(models.Model):
    name = models.CharField(verbose_name="Kafedra nomi: ", max_length=250, null=True, blank=True)
    code = models.CharField(verbose_name="Kafedra kodi: ", max_length=100, null=True, blank=True)
    volume = models.IntegerField(null=True, blank=True)
    auditorium_type = models.ForeignKey(AuditoriumType,on_delete=models.SET_NULL, null=True, blank=True)
    building = models.ForeignKey(Building, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


