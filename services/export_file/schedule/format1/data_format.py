from models.models.answer import AnswerDetail
from django.db.models import Count, Q
from models.models.survey import Survey, SurveyQuestion, SurveyAnswerOption


def export_file_schedule_format1_data_format(schedules, survey):
    schedule_ids = list(schedules.values_list("id", flat=True))

    # 🔥 BIRTA YIRIK QUERY — HAMMA COUNTLAR!
    answer_details = (
        AnswerDetail.objects
        .filter(answer__schedule_id__in=schedule_ids)
        .values(
            "answer__schedule_id",
            "survey_question_id",
            "survey_answer_option_id"
        )
        .annotate(total=Count("id"))
    )

    # mapping → {(schedule_id, question_id, option_id): count}
    answer_map = {
        (a["answer__schedule_id"], a["survey_question_id"], a["survey_answer_option_id"]): a["total"]
        for a in answer_details
    }

    # savollarni olish
    questions = SurveyQuestion.objects.filter(survey=survey).order_by("order_position")
    questions_list = list(questions)

    # optionsni olish
    options_map = {}
    for q in questions_list:
        options_map[q.id] = list(
            SurveyAnswerOption.objects.filter(question=q).order_by("type")
        )

    # Schedules → export data
    export_data = []
    for s in schedules:
        one_schedule = {
            "schedule": s,
            "questions_and_answer_count": []
        }
        for q in questions_list:
            answers = []
            for opt in options_map[q.id]:
                count_val = answer_map.get((s.id, q.id, opt.id), 0)
                answers.append({
                    "id": opt.id,
                    "name": opt.name,
                    "type": opt.type,
                    "send_count": count_val
                })
            one_schedule["questions_and_answer_count"].append({
                "question_id": q.id,
                "answers": answers
            })
        export_data.append(one_schedule)

    return export_data