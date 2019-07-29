from django.core.management.base import BaseCommand
from evaluation.models import Evaluation
import csv
from datetime import datetime
from tqdm import tqdm


class Command(BaseCommand):
    help = "Create a CSV file with all evaluations and their associated recordings." \
           "Can be filtered based on the latest date using --date."

    def add_arguments(self, parser):
        parser.add_argument('-f', '--file', type=str, help='File path.')
        parser.add_argument('-d', '--date', type=str, help='Date range in dd/mm/yyyy.')

    def handle(self, *args, **options):
        # File path
        user_file = options['file']
        csv_file_path = user_file if user_file else 'evaluations.csv'

        # Date
        date_arg = options['date']
        if date_arg:
            requested_date = datetime.strptime(date_arg, '%d/%m/%Y')
            eval_objects = Evaluation.objects.filter(
                    associated_recording__timestamp__lte=requested_date)
        else:
            eval_objects = Evaluation.objects.all()

        # Collect
        with open(csv_file_path, 'w') as f:
            csv_writer = csv.writer(f)
            csv_writer.writerow(['Timestamp', 'Session ID', 'Recording ID', 'Surah',
                                 'Ayah', 'URL', 'Evaluation', 'Platform'])
            for eval_object in tqdm(eval_objects):
                csv_writer.writerow([
                    eval_object.associated_recording.timestamp,
                    eval_object.session_id,
                    eval_object.associated_recording.id,
                    eval_object.associated_recording.surah_num,
                    eval_object.associated_recording.ayah_num,
                    eval_object.associated_recording.file.url,
                    eval_object.evaluation,
                    eval_object.platform
                ])
