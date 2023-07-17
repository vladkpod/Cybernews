import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import GridSearchCV
from data_cleaner import clean_data
from data_cleaner import clean_text, preprocess_text

def train_and_validate_model():
    # Call the cleaning function from the reader.py file
    cleaned_data = clean_data()
    
    # Convert text data to numerical data using TF-IDF
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(cleaned_data['summary'])
    y = cleaned_data['source']
    
    # Save the vectorizer for later use
    with open('vectorizer.pkl', 'wb') as f:
        pickle.dump(vectorizer, f)
        
    # Convert categorical labels to numerical values
    label_encoder = LabelEncoder()
    y = label_encoder.fit_transform(y)
    
    # Save the label encoder for later use
    with open('label_encoder.pkl', 'wb') as f:
        pickle.dump(label_encoder, f)
    
    # Split the data into training and validation sets
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)
    
   # Train the model with hyperparameter tuning and class balancing
    parameters = {'C': [0.1, 1, 10], 'penalty': ['l1', 'l2']}
    model = GridSearchCV(LogisticRegression(class_weight='balanced', solver='liblinear', max_iter=1000), parameters, cv=5)
    model.fit(X_train, y_train)

    
    # Save the model for later use
    with open('model.pkl', 'wb') as f:
        pickle.dump(model, f)
    
    # Validate the model
    y_pred = model.predict(X_val)
    
    # Print the evaluation metrics
    print(f'Accuracy: {accuracy_score(y_val, y_pred)}')
    print(f'Precision: {precision_score(y_val, y_pred, average="weighted", zero_division=0)}')
    print(f'Recall: {recall_score(y_val, y_pred, average="weighted")}')
    print(f'F1 Score: {f1_score(y_val, y_pred, average="weighted")}')

if __name__ == '__main__':
    train_and_validate_model()

def load_model(model_file):
    with open(model_file, 'rb') as f:
        model = pickle.load(f)
    return model

model = load_model('model.pkl')

import pickle

def load_model(model_file):
    with open(model_file, 'rb') as f:
        model = pickle.load(f)
    return model

def preprocess_article(article):
    # Apply the same preprocessing steps as used during training
    cleaned_text = clean_text(article)  # Use the cleaning function from the data_cleaner.py file
    preprocessed_text = preprocess_text(cleaned_text)  # Apply additional preprocessing steps if needed
    return preprocessed_text

def predict_category(article):
    preprocessed_article = preprocess_article(article)
    prediction = model.predict([preprocessed_article])[0]
    return prediction

if __name__ == '__main__':
    model = load_model('model.pkl')