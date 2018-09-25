(ns newsfrt.core
  (:require [reagent.core :as reagent]
            [re-frame.core :as rf]
            [newsfrt.events :as events]
            [newsfrt.views :as views]
            [newsfrt.config :as config]))


(defn dev-setup []
  (when config/debug?
    (enable-console-print!)
    (println "dev mode")))

(defn mount-root []
  (rf/clear-subscription-cache!)
  (reagent/render [views/setup-main-panel]
                  (.getElementById js/document "app")))

(defn ^:export init []
  (rf/dispatch-sync [::events/initialize-db])
  (dev-setup)
  (mount-root)
  #_(rf/dispatch [:initialize-content]))
