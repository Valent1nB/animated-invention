from enum import StrEnum


class UserRole(StrEnum):
    intern = "intern"
    mentor = "mentor"
    head_mentor = "head_mentor"
    superuser = "superuser"


class Role(StrEnum):
    mentor = "mentor"
    head_mentor = "head_mentor"
    superuser = "superuser"


class InternshipStatus(StrEnum):
    awaited = "awaited"
    active = "active"
    paused = "paused"
    for_sale = "for_sale"
    sold = "sold"
    laid_off = "laid_off"


class EnglishLevel(StrEnum):
    A2 = "A2"
    B1 = "B1"
    B2 = "B2"
    C1 = "C1"
    C2 = "C2"
    other = "other"


class EmploymentStatus(StrEnum):
    student = "student"
    employed = "employed"
    unemployed = "unemployed"
    other = "other"


class MilitaryStatus(StrEnum):
    subject_to_conscription = "subject_to_conscription"
    not_subject_to_conscription = "not_subject_to_conscription"
    possible_call_ups = "possible_call_ups"


class MentorSort(StrEnum):
    full_name = "full_name"
    interns_active = "interns_active"
    available = "available"
    available_for_interview = "available_for_interview"
    role = "role"
    city = "city"
    email = "email"


class InternSort(StrEnum):
    full_name = "full_name"
    status = "status"
    start_date = "start_date"
    end_date = "end_date"
    internship_length = "internship_length"
    city = "city"
    email = "email"
    employment_status = "employment_status"
    english_level = "english_level"
    university_name = "university_name"
    ready_for_sale = "ready_for_sale"
    military_status = "military_status"


class RequestTopic(StrEnum):
    other = "other"
    give_cv = "give_cv"
    add_to_checks = "add_to_checks"
    create_aws_acc = "create_aws_acc"
    more_interns_needed = "more_interns_needed"


class RequestStatus(StrEnum):
    created = "created"
    in_progress = "in_progress"
    canceled = "canceled"
    completed = "completed"


class RequestSort(StrEnum):
    created_at = "created_at"
    status = "status"
    topic = "topic"


class Permission(StrEnum):
    mentor_get = "mentor_get"
    mentor_get_self = "mentor_get_self"
    mentor_get_head = "mentor_get_head"
    mentor_get_all = "mentor_get_all"
    mentor_update = "mentor_update"
    mentor_update_self = "mentor_update_self"
    mentor_archive = "mentor_archive"
    mentor_recover = "mentor_recover"
    mentor_create = "mentor_create"

    intern_get = "intern_get"
    intern_get_all = "intern_get_all"
    intern_get_stats = "intern_get_stats"
    intern_create = "intern_create"
    intern_update = "intern_update"
    intern_reassign_mentor = "intern_reassign_mentor"

    request_get = "request_get"
    request_get_all = "request_get_all"
    request_create = "request_create"
    request_update = "request_update"
    request_update_self = "request_update_self"

    unit_get_all = "unit_get_all"

    @classmethod
    def basic_intern_permissions(cls) -> set["Permission"]:
        return set()

    @classmethod
    def mentor_permissions(cls) -> set["Permission"]:
        intern_permissions_set = cls.basic_intern_permissions()
        mentor_permissions_set = intern_permissions_set.union(
            {
                Permission.mentor_update_self,
                Permission.mentor_get_self,
                Permission.mentor_get_head,
                Permission.intern_get,
                Permission.intern_get_all,
                Permission.intern_get_stats,
                Permission.intern_update,
                Permission.request_get,
                Permission.request_get_all,
                Permission.request_create,
                Permission.request_update_self,
            }
        )
        return mentor_permissions_set

    @classmethod
    def head_mentor_permissions(cls) -> set["Permission"]:
        mentor_permissions_set = cls.mentor_permissions()
        head_mentor_permissions_set = mentor_permissions_set.union(
            {
                Permission.mentor_update,
                Permission.mentor_archive,
                Permission.mentor_recover,
                Permission.mentor_create,
                Permission.mentor_get_all,
                Permission.intern_get,
                Permission.intern_create,
                Permission.intern_reassign_mentor,
                Permission.request_update,
            }
        )
        return head_mentor_permissions_set

    @classmethod
    def superuser_permissions(cls) -> set["Permission"]:
        return set(permission for permission in cls)
