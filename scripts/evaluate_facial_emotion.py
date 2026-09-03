"""
Chuwi Facial Emotion Evaluation

Generates evaluation metrics after training:
- accuracy
- precision
- recall
- F1-score
- confusion matrix
"""

from sklearn.metrics import classification_report, confusion_matrix, accuracy_score


def evaluate_predictions(y_true, y_pred, classes):
    print('Accuracy:', accuracy_score(y_true, y_pred))
    print(classification_report(y_true, y_pred, target_names=classes))
    print('Confusion Matrix:')
    print(confusion_matrix(y_true, y_pred))


if __name__ == '__main__':
    print('Evaluation module ready for Chuwi FacialEmotionModel')
