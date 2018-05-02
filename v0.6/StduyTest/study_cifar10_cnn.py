'''Train a simple deep CNN on the CIFAR10 small images dataset.

It gets to 75% validation accuracy in 25 epochs, and 79% after 50 epochs.
(it's still underfitting at that point, though).
'''

from __future__ import print_function
import keras
from keras.datasets import cifar10
from keras.preprocessing.image import ImageDataGenerator
from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation, Flatten
from keras.layers import Conv2D, MaxPooling2D
import os

batch_size = 32     #批尺度——梯度下降法
                    # batch_size=1 
                    # batch_size=N ( N为总数量 ) 
                    # batch_size=n ( n < N )

num_classes = 10    #
epochs = 100        #
data_augmentation = True
num_predictions = 20
save_dir = os.path.join(os.getcwd(), 'saved_models')
model_name = 'keras_cifar10_trained_model.h5'

# The data, split between train and test sets: 
# 数据分为训练集和测试集：
(x_train, y_train), (x_test, y_test) = cifar10.load_data()
print('x_train shape:', x_train.shape)
print(x_train.shape[0], 'train samples')
print(x_test.shape[0], 'test samples')

# Convert class vectors to binary class matrices.
# 将类向量转换为二进制类矩阵。
y_train = keras.utils.to_categorical(y_train, num_classes)
y_test = keras.utils.to_categorical(y_test, num_classes)

model = Sequential()
model.add(Conv2D(32, (3, 3), padding='same',
                 input_shape=x_train.shape[1:]))
model.add(Activation('relu'))
model.add(Conv2D(32, (3, 3)))
model.add(Activation('relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Dropout(0.25))

model.add(Conv2D(64, (3, 3), padding='same'))
model.add(Activation('relu'))
model.add(Conv2D(64, (3, 3)))
model.add(Activation('relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Dropout(0.25))

model.add(Flatten())
model.add(Dense(512))
model.add(Activation('relu'))
model.add(Dropout(0.5))
model.add(Dense(num_classes))
model.add(Activation('softmax'))

# initiate RMSprop optimizer
# 启动RMSprop优化器
opt = keras.optimizers.rmsprop(lr=0.0001, decay=1e-6)

# Let's train the model using RMSprop
# 我们使用RMSprop来训练模型
model.compile(loss='categorical_crossentropy',
              optimizer=opt,
              metrics=['accuracy'])

x_train = x_train.astype('float32')
x_test = x_test.astype('float32')
x_train /= 255
x_test /= 255

if not data_augmentation:
    print('Not using data augmentation.')
    model.fit(x_train, y_train,
              batch_size=batch_size,
              epochs=epochs,
              validation_data=(x_test, y_test),
              shuffle=True)
else:
    print('Using real-time data augmentation.')
    # This will do preprocessing and realtime data augmentation:
    # 这将做预处理和实时数据增强：
        # 在深度学习中，我们经常需要用到一些技巧(比如将图片进行旋转，翻转等)来进行data augmentation, 来减少过拟合。
    datagen = ImageDataGenerator(
        featurewise_center=False,  # set input mean to 0 over the dataset
                                   # 在数据集上设置输入均值为0
        samplewise_center=False,  # set each sample mean to 0
                                  # 将每个样本均值设置为0
        featurewise_std_normalization=False,  # divide inputs by std of the dataset
                                              # 按照数据集的std(标准)分割输入
        samplewise_std_normalization=False,  # divide each input by its std
                                             #
        zca_whitening=False,  # apply ZCA whitening
                              #
                              
        rotation_range=0,  # randomly rotate images in the range (degrees, 0 to 180)
                           # 整数，数据提升时图片随机转动的角度
        width_shift_range=0.1,  # randomly shift images horizontally (fraction of total width)
                                # 浮点数，图片宽度的某个比例，数据提升时图片水平偏移的幅度`
        height_shift_range=0.1,  # randomly shift images vertically (fraction of total height)
                                 # 浮点数，图片高度的某个比例，数据提升时图片竖直偏移的幅度
        horizontal_flip=True,  # randomly flip images
                               # 布尔值，进行随机水平翻转
        vertical_flip=False  # randomly flip images
                             # 布尔值，进行随机竖直翻转
    )

    # Compute quantities required for feature-wise normalization
    # 计算功能所需的标准化所需的数量
    # (std, mean, and principal components if ZCA whitening is applied).
    # (如果应用ZCA白化，则为标准，平均和主要成分).
    datagen.fit(x_train)

    # Fit the model on the batches generated by datagen.flow().
    # 将模型放在由 datagen.flow() 生成的批处理上。
    model.fit_generator(datagen.flow(x_train, y_train,
                                     batch_size=batch_size),
                        epochs=epochs,
                        validation_data=(x_test, y_test),
                        workers=4)

# Save model and weights
# 保存模型和权重
if not os.path.isdir(save_dir):
    os.makedirs(save_dir)
model_path = os.path.join(save_dir, model_name)
model.save(model_path)
print('Saved trained model at %s ' % model_path)

# Score trained model.
# 评分训练模型
scores = model.evaluate(x_test, y_test, verbose=1)
print('Test loss:', scores[0])
print('Test accuracy:', scores[1])
