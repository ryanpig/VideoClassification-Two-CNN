# version 2
# to build a 3ch CNN model
#from readfunc import ReadData
from readfunc_v2 import readData

import numpy as np
import tensorflow as tf

tf.logging.set_verbosity(tf.logging.INFO)

def cnn_model_fn(features, labels, mode):
  # in,c1,p1,c2,p2,flat,dense,drop,logits

  input_layer = tf.reshape(features["x"], [-1, 120, 120, 3]) # -1,28,28,1
  conv1 = tf.layers.conv2d(
      inputs=input_layer,
      filters=32,
      kernel_size=[5, 5],
      padding="same",
      activation=tf.nn.relu)
  pool1 = tf.layers.max_pooling2d(inputs=conv1, pool_size=[2, 2], strides=2)
  conv2 = tf.layers.conv2d(
      inputs=pool1,
      filters=64,
      kernel_size=[5, 5],
      padding="same",
      activation=tf.nn.relu)
  pool2 = tf.layers.max_pooling2d(inputs=conv2, pool_size=[2, 2], strides=2)
  pool2_flat = tf.reshape(pool2, [-1, 30 * 30 * 64 * 1])
  dense = tf.layers.dense(inputs=pool2_flat, units=128, activation=tf.nn.relu)
  dropout = tf.layers.dropout(
      inputs=dense, rate=0.4, training=mode == tf.estimator.ModeKeys.TRAIN)

  logits = tf.layers.dense(inputs=dropout, units=5)

  predictions = {
      "classes": tf.argmax(input=logits, axis=1,name="predication_classes"),
      "probabilities": tf.nn.softmax(logits, name="softmax_tensor")
  }
  if mode == tf.estimator.ModeKeys.PREDICT:
    return tf.estimator.EstimatorSpec(mode=mode, predictions=predictions)

  #loss
  loss = tf.losses.sparse_softmax_cross_entropy(labels=labels, logits=logits)

  # Configure the Training Op (for TRAIN mode)
  if mode == tf.estimator.ModeKeys.TRAIN:
    optimizer = tf.train.GradientDescentOptimizer(learning_rate=0.001)
    train_op = optimizer.minimize(
        loss=loss,
        global_step=tf.train.get_global_step())
    return tf.estimator.EstimatorSpec(mode=mode, loss=loss, train_op=train_op)

  # Add evaluation metrics (for EVAL mode)
  m_confusion = tf.confusion_matrix(labels,predictions["classes"], 5)

  eval_metric_ops = {
      "accuracy": tf.metrics.accuracy(
          labels=labels, predictions=predictions["classes"])}


  # predi = predictions["classes"] , one batch results in two predictions [3 3]
  # Save them and make confusion_matrix, outside of function.

  #comfusion = tf.confusion_matrix(labels=labels,predictions=predi,
                                  #num_classes=5,name='confusionMat')
  return tf.estimator.EstimatorSpec(
      mode=mode, loss=loss, eval_metric_ops=eval_metric_ops)


#def main(unused_argv):
# Load training and eval data
'''
un = 1
train1, test1 = ReadData(un)
train_data = train1.images
train_labels = np.asarray(train1.labels, dtype=np.int32)
eval_data = test1.images
eval_labels = np.asarray(test1.labels, dtype=np.int32)
'''
train1,eval1, test1 = readData()
train_data = train1.images
train_labels = train1.labels
eval_data = eval1.images
eval_labels = eval1.labels
test_data = test1.images
test_labels =  test1.labels


print(np.shape(train_data))
print(np.shape(eval_data))
print(train_labels)

# Create the Estimator
action_classifier = tf.estimator.Estimator(
  model_fn=cnn_model_fn, model_dir="/tmp/mnist_convnet_model9")

# Set up logging for predictions
# Log the values in the "Softmax" tensor with label "probabilities"
tensors_to_log = {"probabilities": "softmax_tensor",
                "classes": "predication_classes"}
logging_hook = tf.train.LoggingTensorHook(
  tensors=tensors_to_log, every_n_iter=50)

# Train the model
train_input_fn = tf.estimator.inputs.numpy_input_fn(
  x={"x": train_data},
  y=train_labels,
  batch_size=2,
  num_epochs=2,
  shuffle=True)
action_classifier.train(
  input_fn=train_input_fn,
  steps=10, #20000
  hooks=[logging_hook])

# Evaluate the model by training data
eval_Tr_input_fn = tf.estimator.inputs.numpy_input_fn(
  x={"x": train_data},
  y=train_labels,
  batch_size=32,
  num_epochs=2,
  shuffle=True)
eval_Tr_results = action_classifier.evaluate(input_fn=eval_Tr_input_fn)
print("Evaluate Training data:", eval_Tr_results)

# Evaluate the model by evaluating data
eval_input_fn = tf.estimator.inputs.numpy_input_fn(
  x={"x": eval_data},
  y=eval_labels,
  batch_size=32,
  num_epochs=2,
  shuffle=True)
eval_results = action_classifier.evaluate(input_fn=eval_input_fn)
print("Evaluate Evaluating data:",eval_results)

# Testing the model by filmed video.
test_input_fn = tf.estimator.inputs.numpy_input_fn(
  x={"x": test_data},
  y=test_labels,
  batch_size=1,
  num_epochs=2,
  shuffle=True)
test_results = action_classifier.evaluate(input_fn=test_input_fn)
print("Evaluate Testing data:",test_results)


# The shape of each layer in CNN model
#for tmp in  action_classifier.get_variable_names():
#    print(np.shape(action_classifier.get_variable_value(name=tmp)))


#if __name__ == "__main__":
#  tf.app.run()