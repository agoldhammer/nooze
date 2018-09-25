(ns newsfrt.db
  (:require [cljs-time.core :refer [now]]))

(def default-db
  {:name "re-frame"
   :default-set true
   :show-custom-time-panel? false
   :cats-loading? false
   :dummy-list {:source "TweetDeck"
                :created_at "1/1/01"
                :author "NYTimes"
                :text "This is dummy text for testing. Making it longer, just for fun. Today the president announced nothing. http://prospect.org"}
   :custom-query {:text ""
                  :status :success
                  }
   :custom-date {:start (now)
                 :end   (now)}
   :time-button-bar {:active :tb0
                     :ids {:tb0 ["3 hrs" "-H 3"]
                           :tb1 ["6 hrs" "-H 6"]
                           :tb2 ["12 hrs" "-H 12"]
                           :tb3 ["1 day" "-d 1"]
                           :tb4 ["2 days" "-d 2"]
                           :tb5 ["3 days" "-d 3"]
                           :tb6 ["Custom" :custom]}}})
