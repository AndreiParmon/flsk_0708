from app import db, create_app  # ваш объект SQLAlchemy

def reset_database():
    app = create_app()               # создаём экземпляр Flask-приложения
    with app.app_context():          # открываем контекст приложения
        db.drop_all()                # удаляем все таблицы
        db.create_all()              # создаём таблицы заново
        print("База данных сброшена")

if __name__ == "__main__":
    reset_database()
