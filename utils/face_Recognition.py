import os
from tkinter import messagebox

import face_recognition
from deepface import DeepFace

# global metrics
# metrics = ["cosine", "euclidean", "euclidean_l2"]
models = ["Facenet", 
          "VGG-Face", "ArcFace"]
        #   "Dlib", "Facenet512", "OpenFace", "DeepFace", "DeepID", "ArcFace", "Dlib", "SFace"]
# global backends
# backends = ['opencv', 'ssd', 'dlib', 'mtcnn', 'retinaface', 'mediapipe']

class face_Recognition:
    def __init__(self, peoplelist, platform, mode, threshold = 0.6):
        if threshold == "superstrict":
            threshold = 0.40
        if threshold == "strict":
            threshold = 0.50
        if threshold == "standard":
            threshold = 0.60
        if threshold == "loose":
            threshold = 0.70

        self.threshold = threshold
        self.peoplelist = peoplelist
        self.platform = platform
        self.mode = mode #"fast", "accurate"

        print("[Face Recognition] Initializing process...")
        print("[Face Recognition] People in line {} for Platform {}".format(len(self.peoplelist), self.platform))

        self.user_face_recognition_new()

    def user_face_recognition_new(self):

        results_people = []

        for person in self.peoplelist:
            list_user_to_compare = []
            if 'facebook' in self.platform:
                list_user_to_compare = person.list_candidate_user_found_fb
            elif 'instagram' in self.platform:
                list_user_to_compare = person.list_candidate_user_found_instagram
            elif 'linkedin' in self.platform:
                list_user_to_compare = person.list_candidate_user_found_linkedin
            elif 'X' in self.platform:
                list_user_to_compare = person.list_candidate_user_found_X
            elif 'threads' in self.platform:
                list_user_to_compare = person.list_candidate_user_found_threads

            print(f"[Face Recognition] list_user_to_compare for {person.full_name}: " , [c.candidate_to_dict()['username'] for c in list_user_to_compare])
            if len(list_user_to_compare) > 0:
                print(f"[Face Recognition] People to compare with {person.full_name}: ",len(list_user_to_compare))

                person = self.scan_list_user_to_compare(list_user_to_compare=list_user_to_compare, person=person, threshold=self.threshold)

                if person.social_profiles[self.platform]['Face_Recognition_Result'] != '' or person.social_profiles[self.platform]['Face_Recognition_Result'] != None:
                    print('[Face Recognition] A person was found for {}!'.format(person.full_name))
                else:
                    print('[Face Recognition] No matches were found for {}!'.format(person.full_name))
            else:
                print(f'[Face Recognition] No matches were found for {person.full_name}!')

            results_people.append(person)

        print("[Face Recognition] End Process...\n")

        self.peoplelist = results_people

    def scan_list_user_to_compare(self, list_user_to_compare, person, threshold):
        self.threshold = threshold

        maximum_matching_score = -1

        models_to_use = ''

        if self.mode == 'fast':
            models_to_use = [models[0]]
        elif self.mode == 'accurate':
            models_to_use = models

        # for user_name, url_profile, url_image_user, local_path_img in list_user_to_compare:
        for candidate in list_user_to_compare:
            user_name = candidate.get_username()
            url_profile = candidate.get_url_profile()
            url_image_user = candidate.get_link_image()
            local_path_img = candidate.get_local_path_img()

            if not os.path.exists(local_path_img):
                print("[Face Recognition] ",local_path_img," does not exist\n")
            else:

                print("[Face Recognition] threshold ",self.threshold,
                    " - original_person_image ",person.original_person_image,
                    " - local_path_img",local_path_img,
                    " - user_name",user_name, '\n\n')
                
                try:
                    
                    models_resut = []
                    result = None

                    for model in models_to_use:

                            models_resut.append(DeepFace.verify(
                                img1_path = person.original_person_image,
                                img2_path = local_path_img,
                                model_name = model,
                                enforce_detection=False,
                            )['distance'])
                    
                    match = False
                    
                    if len(models_to_use) > 1:
                        above_threshold = sum(value > threshold for value in models_resut)
                        if above_threshold > len(models_resut) / 2:
                            maximum_matching_score = [value > threshold for value in models_resut]
                            match = True

                    elif len(models_to_use) == 1:
                        result = float(models_resut[0])
                        if result >= self.threshold:
                            if result >= maximum_matching_score:
                                maximum_matching_score = result
                                match = True

                    if match:
                        person.social_profiles[self.platform]['username'] = user_name
                        person.social_profiles[self.platform]['profile'] = url_profile
                        person.social_profiles[self.platform]['image'] = local_path_img
                        person.social_profiles[self.platform]['Link_image'] = url_image_user
                        person.social_profiles[self.platform]['Face_Recognition_Result'] = maximum_matching_score

                except Exception as e:
                    raise Exception('[Face Recognition]', f"Face Recognition Error: {e}")
            
        return person

    def user_face_recognition_original(self):

        print("[Face Recognition] People in line {}\n".format(len(self.peoplelist)))
        print("[Face Recognition] Platform {}\n".format(self.platform))
        results_people = []

        for person in self.peoplelist:
            list_user_to_compare = []
            if 'facebook' in self.platform:
                list_user_to_compare = person.list_candidate_user_found_fb
            elif 'instagram' in self.platform:
                list_user_to_compare = person.list_candidate_user_found_instagram
            elif 'linkedin' in self.platform:
                list_user_to_compare = person.list_candidate_user_found_linkedin
            elif 'X' in self.platform:
                list_user_to_compare = person.list_candidate_user_found_X
            elif 'threads' in self.platform:
                list_user_to_compare = person.list_candidate_user_found_threads

            print("[Face Recognition] list_user_to_compare: ",[c.candidate_to_dict()['username'] for c in list_user_to_compare],'\n')
            target_image = face_recognition.load_image_file(person.original_person_image)

            target_encoding = None
            try:
                if target_image:
                    target_encoding = face_recognition.face_encodings(target_image)[0]
                    print("[Face Recognition] target_encoding Done!\n")#, target_encoding)
            except:
                messagebox.showinfo('Info', "L immagine come Input sembra non avere volti. Usa un'altra immagine come input")
                continue

            for candidate in list_user_to_compare:
                user_name = candidate.get_username()
                url_profile = candidate.get_url_profile()
                url_image_user = candidate.get_link_image()
                local_path_img = candidate.get_local_path_img()
                potential_target_image = None
                potential_target_encoding = None
                try:
                    if local_path_img:
                        potential_target_image = face_recognition.load_image_file(local_path_img)
                except Exception as e:
                    messagebox.showerror('Error', f'Errore nel Face Recognition\n{e}')

                try:  # try block for when an image has no faces
                    if potential_target_image:
                        potential_target_encoding = face_recognition.face_encodings(potential_target_image)[0]
                except:
                    #messagebox.showinfo('Info', 'L immagine sembra non avere volti')
                    continue

                results = None
                try:
                    if target_encoding and potential_target_encoding:
                        results = face_recognition.face_distance([target_encoding], potential_target_encoding)
                except:
                    #messagebox.showinfo('Info', 'L immagine sembra non avere volti')
                    continue

                print("[Face Recognition] Results",results,'\n')

            maximum_matching_score = -1

            # for user_name, url_profile, url_image_user, local_path_img in list_user_to_compare:
            # for user_name, url_profile, url_image_user, local_path_img in list_user_to_compare:
            for candidate in list_user_to_compare:
                user_name = candidate.get_username()
                url_profile = candidate.get_url_profile()
                url_image_user = candidate.get_url_image_user()
                local_path_img = candidate.get_local_path_img()
                potential_target_image = None
                potential_target_encoding = None
                results = None

                if not os.path.exists(local_path_img):
                    print("[Face Recognition] ",local_path_img,"does not exist\n")
                else:
                    #print("[Face Recognition]",local_path_img,"Exist!")
                    try:
                        if local_path_img:
                            potential_target_image = face_recognition.load_image_file(local_path_img)
                    except Exception as e:
                        messagebox.showerror('Error', f'Errore nel Face Recognition\n{e}')

                    try:  # try block for when an image has no faces
                        if potential_target_image:
                            potential_target_encoding = face_recognition.face_encodings(potential_target_image)[0]
                    except:
                        #messagebox.showinfo('Info', 'L immagine sembra non avere volti')
                        print("[Face Recognition] Info",'L immagine sembra non avere volti\n')
                        continue

                    try:
                        if potential_target_encoding and target_encoding:
                            results = face_recognition.face_distance([target_encoding], potential_target_encoding)
                    except:
                        print("[Face Recognition] Info face_distance",'L immagine sembra non avere volti\n')
                        #messagebox.showinfo('Info', 'L immagine sembra non avere volti')
                        continue

                    if results:
                        match = False
                        result = max(results)
                        print("[Face Recognition] threshold",self.threshold,
                              " - result",result,
                              " - maximum_matching_score",maximum_matching_score,
                              " - user_name",user_name, '\n')

                        print('result',result, '- type:', type(result))
                        print('self.threshold',self.threshold, '- type:', type(self.threshold))
                        print('if result >= self.threshold', result >= self.threshold)

                        if result >= self.threshold:
                            if result >= maximum_matching_score:
                                maximum_matching_score = result
                                print('[Face Recognition] person.social_profiles[self.platform]',person.social_profiles[self.platform])
                                print('*'*30)
                                person.social_profiles[self.platform]['username'] = user_name
                                person.social_profiles[self.platform]['profile'] = url_profile
                                person.social_profiles[self.platform]['image'] = local_path_img
                                person.social_profiles[self.platform]['Link_image'] = url_image_user
                                person.social_profiles[self.platform]['Face_Recognition_Result'] = result
                            self.threshold = result
                            match = True

                        if match: print('A person was found for {}!\n'.format(user_name))
                        else: print('No matches were found for {}!\n'.format(user_name))
        
            results_people.append(person)

        self.peoplelist = results_people

    def get_face_recognition_results(self):
        return self.peoplelist

