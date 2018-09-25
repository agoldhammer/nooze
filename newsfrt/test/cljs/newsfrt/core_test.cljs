(ns newsfrt.core-test
  (:require [cljs.test :refer-macros [deftest testing is async]]
            [clojure.string :as string]
            [cljs.core.async :refer [chan close!]]
            [newsfrt.core :as core]
            [re-frame.core :as rf]
            [day8.re-frame.test :as rf-test]
            [newsfrt.events :as events]
            [newsfrt.subs :as subs])
  (:require-macros
    [cljs.core.async.macros :as m :refer [go]])
  )

;;  run with lein doo phantom test

(defn timeout [ms]
  (let [c (chan)]
    (js/setTimeout (fn [] (close! c)) ms)
    c))

(deftest basic--sync
  (rf-test/run-test-sync
    ;;  (test-fixtures)
    (rf/dispatch [::events/initialize-db])
    ;; (rf/dispatch [:initialize-content])
    (testing "name for sanity"
      (let [name @(rf/subscribe [::subs/name])]
        (println "name" name)
        (is (= name "re-frame"))))

    (testing "formatted date"
      (let [fdate @(rf/subscribe [:get-formatted-custom-date])]
        (println "formatted date: " fdate)
        (is (string/starts-with? fdate "-s"))))))

#_(deftest basic--async
  (rf-test/run-test-async
    ;; (test-fixtures)
    (rf/dispatch-sync [::events/initialize-db])
    (rf/dispatch-sync [:initialize-content])
    (rf-test/wait-for [:got-recent])
    (go (timeout 1000))
    (testing "name for sanity"
      (let [name @(rf/subscribe [::subs/name])
            cats @(rf/subscribe [:categories])]
        (println "name" name)
        (println "categs are " cats)
        (is (= name "re-frame"))))

    (testing "time button"
      (rf/dispatch-sync [:set-active-time-button :tb2])
      (is (= :tb2 @(rf/subscribe [:time-button-active-id]))))

    (testing "item count"
     (is (> @(rf/subscribe [:item-count]) 0)))

    (testing "categories"
      (let [cats @(rf/subscribe [:categories])]
        (println "cats are" cats)
        (is (some #{:Culture} cats))))
    ))


;; (deftest item-count-test
;;   (testing "item count"
;;     (is (> @(rf/subscribe [:item-count]) 0))))

;; (deftest cats-loading
;;   (testing "cats loading"
;;     (is (not @(rf/subscribe [:cats-loading?])))))


;; (deftest categories
;;   (rf/dispatch-sync [:initialize-content])
;;   (go (<! (timeout 6000)))
;;   (let [cats @(rf/subscribe [:categories])]
;;     (println "Categories" cats)
;;     (is (some #{:Culture} cats))))

;; Read this
;; https://github.com/bensu/doo/wiki/End-to-end-testing-example
;; https://clojurescript.org/tools/testing
;; https://github.com/Day8/re-frame-test
