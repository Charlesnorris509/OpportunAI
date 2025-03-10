# migrations.py
from django.db import migrations, models
import django.db.models.deletion
from pgvector.django import VectorField

class Migration(migrations.Migration):
    initial = True
    
    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    def create_vector_extension(apps, schema_editor):
        schema_editor.execute('CREATE EXTENSION IF NOT EXISTS vector')

    operations = [
        # Create pgvector extension
        migrations.RunPython(create_vector_extension),
        
        # Create UserProfile model with vector field
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(
                    auto_created=True, 
                    primary_key=True, 
                    serialize=False, 
                    verbose_name='ID'
                )),
                ('phone_number', models.CharField(max_length=20, blank=True)),
                ('location', models.CharField(max_length=100, blank=True)),
                ('linkedin_url', models.URLField(blank=True)),
                ('github_url', models.URLField(blank=True)),
                ('portfolio_url', models.URLField(blank=True)),
                ('preferred_job_title', models.CharField(max_length=100, blank=True)),
                ('years_of_experience', models.IntegerField(default=0)),
                ('profile_embedding', VectorField(dimensions=384, null=True)),
                ('user', models.OneToOneField(
                    on_delete=django.db.models.deletion.CASCADE, 
                    to='auth.User'
                )),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'user_profiles',
                'indexes': [
                    migrations.Index(fields=['location'], name='location_idx'),
                    migrations.Index(fields=['preferred_job_title'], name='job_title_idx'),
                ],
            },
        ),
        
        # Add vector similarity search index
        migrations.RunSQL(
            sql="""
            CREATE INDEX user_profile_embedding_idx ON user_profiles 
            USING ivfflat (profile_embedding vector_cosine_ops)
            WITH (lists = 100);
            """,
            reverse_sql="DROP INDEX IF EXISTS user_profile_embedding_idx;"
        ),
        
        # Add timestamp trigger for updated_at
        migrations.RunSQL(
            sql="""
            CREATE OR REPLACE FUNCTION update_updated_at_column()
            RETURNS TRIGGER AS $$
            BEGIN
                NEW.updated_at = CURRENT_TIMESTAMP;
                RETURN NEW;
            END;
            $$ language 'plpgsql';
            
            CREATE TRIGGER update_user_profile_updated_at
                BEFORE UPDATE ON user_profiles
                FOR EACH ROW
                EXECUTE FUNCTION update_updated_at_column();
            """,
            reverse_sql="""
            DROP TRIGGER IF EXISTS update_user_profile_updated_at ON user_profiles;
            DROP FUNCTION IF EXISTS update_updated_at_column();
            """
        ),
    ]
