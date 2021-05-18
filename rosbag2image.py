
import os
import argparse
import cv2
from PIL import Image as pim
import rosbag
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import sensor_msgs.point_cloud2 as pc2
import numpy as np
from tqdm import tqdm
from multiprocessing.dummy import Pool as ThreadPool

def parse_bag(bag_path):
    bag = rosbag.Bag(bag_path, 'r')
    topic_info = bag.get_type_and_topic_info()  

    image_topics = []
    for key,value  in topic_info.topics.items():
        if value.msg_type == "sensor_msgs/Image":
            image_topics.append(key)

    image_topics_dict = {k:v for k, v in enumerate(image_topics)}
    bag.close()
    return image_topics_dict

# def get_topic_verified(img_topics_dict):

#     topic_str = "\n".join(['%s: %s' % (key, value) for (key, value) in img_topics_dict.items()])
#     input_text = raw_input("Detected Image Topics:\n {} \n Input 'all' or the numbers of selected topics separated with SPACE.".format(topic_str))
#     slected_topics = input_test.split(" ")

#     img_topics = []
#     if slected_topics[0] == "all":
#         img_topics = [v for k,v in img_topics_dict.items()]
#     else:
#         img_topics = [v for k,v in img_topics_dict.items() if str(k) in slected_topics]
    
#     # @@@@@@@@@@@@ test
#     # img_topics = [v for k,v in img_topics_dict.items()]

#     return img_topics 


def imgae_extract(bag_path):
    bag = rosbag.Bag(bag_path, 'r')
    bridge = CvBridge()


    for tpc in img_topics:
        out_folder = os.path.join(bag_path.split(".")[-2].replace("bag","image"), tpc.split("/")[-1])
        try:
            os.makedirs(out_folder)
        except:
            pass

        print("Extract images from %s on topic %s into %s" % (bag_path, tpc, out_folder)) 

        # depth image
        if "depth" in tpc:
            count = 0
            for topic, msg, t in tqdm(bag.read_messages(topics=[tpc])):
                cv_img = bridge.imgmsg_to_cv2(msg)
                cv_img = np.uint16(cv_img)

                cv2.imwrite(os.path.join(out_folder, "frame%04i.png" % count), cv_img)
                count += 1
    
        else:
            count = 0
            for topic, msg, t in tqdm(bag.read_messages(topics=[tpc])):
                cv_img = bridge.imgmsg_to_cv2(msg, desired_encoding="passthrough")      

                # rgb image
                if(len(cv_img.shape) == 3):
                    im_rgb = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
                    im_rgb = cv_img
                    im = pim.fromarray(im_rgb)
                    im.save(os.path.join(out_folder, "frame%04i.png" % count))
                    
                # grey image
                else:
                    cv2.imwrite(os.path.join(out_folder, "frame%04i.png" % count), cv_img)                
                count += 1      

    bag.close()



# main()
parser = argparse.ArgumentParser(description="Extract images from one or multiple rosbags.")
parser.add_argument("input_path", help="Input a rosbag path or a  directory of rosbags")

args = parser.parse_args()
input_path = args.input_path

if os.path.isfile(input_path):
    image_topics_dict = parse_bag(input_path)
    img_topics = [v for k,v in image_topics_dict.items()]

    imgae_extract(input_path)
     
elif os.path.isdir(input_path):
    for subdir, dirs, files in os.walk(input_path):
        # img_topic = []
        for i, file in enumerate(files):
            bag_path = os.path.join(subdir, file)

            image_topics_dict = parse_bag(bag_path)
            img_topics = [v for k,v in image_topics_dict.items()]

            imgae_extract(bag_path)
