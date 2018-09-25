(ns newsfrt.subs
  (:require [re-frame.core :as rf]
            [clojure.string :as string]
            [cljs-time.format  :refer [formatter unparse]]
            ))

(rf/reg-sub
 ::name
 (fn [db]
   (:name db)))

(rf/reg-sub
 :item-count
 (fn [db]
   (get-in db [:navdata :count])))

(rf/reg-sub
 :cats-loading?
 (fn [db]
   (:cats-loading? db)))

(rf/reg-sub
 :recent-loading?
 (fn [db]
   (:recent-loading? db)))

(rf/reg-sub
 :categories
 (fn [db]
   (keys (get-in db [:navdata :cats]))))

(rf/reg-sub
 :category
 (fn [db [_ category]]
   (get-in db [:navdata :cats category])))

(rf/reg-sub
 :topics-by-category
 (fn [db [_ category]]
   (mapv #(:topic %1) (get-in db [:navdata :cats category]))))

(rf/reg-sub
 :topic-descs-by-category
 (fn [db [_ category]]
   (mapv #((juxt :topic :desc) %1) (get-in db [:navdata :cats category]))))

(rf/reg-sub
 :fulltopic
 (fn [db [_ category topic]]
   (let [topics (get-in db [:navdata :cats category])]
     (first (filter #(= topic (:topic %1)) topics)))))

(rf/reg-sub
 :topic-to-query
 (fn [db [_ category topic]]
   (:query @(rf/subscribe [:fulltopic category topic]))))

;; this section is for testing
(defn fake-status-list
  [n db]
  (take n (repeat (:dummy-list db))))

(rf/reg-sub
 :get-authors
 (fn [db]
   (sort (keys @(rf/subscribe [:get-author-display-states])))))

(rf/reg-sub
 :get-author-display-states
 (fn [db]
   (:author-display-states db)))

(rf/reg-sub
 :get-author-display-state
 (fn [db [_ author]]
   (get-in db [:author-display-states author])))

(rf/reg-sub
 :get-fake-status-list
 (fn [db [_ n]]
   (fake-status-list n db)))
;;;;;;;

(rf/reg-sub
 :get-active-authors
 (fn [db]
   (into #{}
         (map first (filter second (:author-display-states db))))))

(rf/reg-sub
 :get-recent
 (fn [db]
   (:recent db)))

(defn status-author-active?
  [status active-authors]
  (some #{(string/upper-case(:author status))} active-authors))

(rf/reg-sub
 :filtered-statuses
 (fn [db]
   (let [active-authors @(rf/subscribe [:get-active-authors])
         statuses (:recent db)]
     (filterv #(status-author-active? %1 active-authors) statuses))))

(rf/reg-sub
 :display-all-authors?
 (fn [db]
   (:display-all-authors? db)))

(rf/reg-sub
 :get-time-button-ids
 (fn [db]
   (keys (get-in db [:time-button-bar :ids]))))

(rf/reg-sub
 :button-id-to-text
 (fn [db [_ button-id]]
   (nth (get-in db [:time-button-bar :ids button-id]) 0)))

(rf/reg-sub
 :query-time
 (fn [db]
   (let [active-time-button @(rf/subscribe [:time-button-active-id])]
     (if (= :tb6 active-time-button)
       @(rf/subscribe [:get-formatted-custom-date])
       (nth (get-in db [:time-button-bar :ids active-time-button]) 1)))))

(rf/reg-sub
 :time-button-active-id
 (fn [db]
   (get-in db [:time-button-bar :active])))


(rf/reg-sub
 :alert?
 (fn [db]
   (:alert db)))

(rf/reg-sub
 :get-custom-query
 (fn [db]
   (get-in db [:custom-query :text])))

(rf/reg-sub
 :get-custom-query-status
 (fn [db]
   (get-in db [:custom-query :status])))

(rf/reg-sub
 :show-custom-time-panel?
 (fn [db]
   (:show-custom-time-panel? db)))

(rf/reg-sub
 :get-custom-date
 (fn [db [_ start-or-end]]
   (get-in db [:custom-date start-or-end])))

(rf/reg-sub
 :get-formatted-custom-date
 (fn [db]
   (let [start @(rf/subscribe [:get-custom-date :start])
         end @(rf/subscribe [:get-custom-date :end])
         stext (unparse (formatter "YYYY-MM-dd") start)
         etext (unparse (formatter "YYYY-MM-dd") end)]
     (str "-s " stext " -e " etext "T23:59:59"))))

(rf/reg-sub
 :default-set?
 (fn [db]
   (:default-set db)))
