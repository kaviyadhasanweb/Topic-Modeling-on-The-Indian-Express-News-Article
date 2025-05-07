import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from gensim import corpora, models
import logging

# Download NLTK resources
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
except Exception as e:
    logging.error(f"Failed to download NLTK resources: {str(e)}")

def preprocess(texts):
    """Preprocess text for topic modeling."""
    try:
        stop_words = set(stopwords.words('english'))
        # Add custom stopwords relevant to news articles
        custom_stopwords = {'said', 'says', 'according', 'reported', 'told', 'would', 'could', 'day', 'today', 'yesterday', 'tomorrow'}
        stop_words.update(custom_stopwords)
        
        processed_texts = []
        for text in texts:
            # Tokenize text
            tokens = word_tokenize(text.lower())
            # Remove stopwords and non-alphabetic tokens
            filtered = [word for word in tokens if word.isalpha() and word not in stop_words and len(word) > 2]
            processed_texts.append(filtered)
        
        return processed_texts
    except Exception as e:
        logging.error(f"Error in text preprocessing: {str(e)}")
        # Return a minimal processed version to prevent complete failure
        return [[word for word in text.lower().split() if len(word) > 2] for text in texts]

def get_topics(processed_texts, num_topics=5):
    """Generate topics using LDA model."""
    try:
        if not processed_texts or all(len(text) == 0 for text in processed_texts):
            raise ValueError("No valid text to process after preprocessing")
            
        # Create dictionary
        dictionary = corpora.Dictionary(processed_texts)
        
        # Filter out extreme values: words appearing in less than 2 documents or more than 50% of documents
        dictionary.filter_extremes(no_below=2, no_above=0.5)
        
        # Create corpus
        corpus = [dictionary.doc2bow(text) for text in processed_texts]
        
        # Train LDA model
        lda_model = models.LdaModel(
            corpus=corpus,
            id2word=dictionary,
            num_topics=num_topics,
            passes=15,  # Increased passes for better convergence
            alpha='auto',
            eta='auto'
        )
        
        # Get topics
        topics = lda_model.print_topics(num_words=5)
        
        # If we didn't get enough topics, create some defaults
        if len(topics) < num_topics:
            default_topics = [
                (i, "topic_terms_unavailable_insufficient_data") 
                for i in range(len(topics), num_topics)
            ]
            topics.extend(default_topics)
            
        return topics
        
    except Exception as e:
        logging.error(f"Error in topic modeling: {str(e)}")
        # Return default topics in case of failure
        return [(i, f"topic_{i+1}_default") for i in range(num_topics)]