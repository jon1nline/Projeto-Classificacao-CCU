from django.core.management.base import BaseCommand
from feedIA.ner import train_ner_model, get_training_examples


class Command(BaseCommand):
    help = 'Treina o modelo NER para extração de entidades médicas'

    def add_arguments(self, parser):
        parser.add_argument(
            '--iterations',
            type=int,
            default=30,
            help='Número de iterações de treinamento (padrão: 30)'
        )

    def handle(self, *args, **options):
        n_iter = options['iterations']
        
        self.stdout.write('Iniciando treinamento do modelo NER...')
        self.stdout.write(f'Iterações: {n_iter}')
        
        training_data = get_training_examples()
        self.stdout.write(f'Exemplos de treinamento: {len(training_data)}')
        
        success, message = train_ner_model(training_data, n_iter=n_iter)
        
        if success:
            self.stdout.write(self.style.SUCCESS(message))
        else:
            self.stdout.write(self.style.ERROR(message))
