from django.contrib import admin

from .models import AnswerChoice, Attempt, Question, Recommendation, Topic


class AnswerChoiceInline(admin.TabularInline):
    model = AnswerChoice
    extra = 2


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('prompt_short', 'topic', 'difficulty', 'created_by', 'created_at')
    list_filter = ('topic', 'difficulty')
    inlines = [AnswerChoiceInline]

    def prompt_short(self, obj):
        return obj.prompt[:60]
    prompt_short.short_description = 'Prompt'


@admin.register(Attempt)
class AttemptAdmin(admin.ModelAdmin):
    list_display = ('student', 'question', 'is_correct', 'time_taken_seconds', 'submitted_at')
    list_filter = ('is_correct', 'question__topic')
    readonly_fields = ('submitted_at',)


@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = ('student', 'topic', 'accuracy_at_generation', 'created_at')
    list_filter = ('topic',)
    readonly_fields = ('created_at',)
