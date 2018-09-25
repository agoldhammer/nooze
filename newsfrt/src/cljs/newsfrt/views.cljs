(ns newsfrt.views
  (:require [re-frame.core :as rf]
            [re-com.core :as re-com]
            [cljs-time.core :refer [now]]
            [cljs-time.coerce  :refer [to-local-date]]
            [cljs-time.format  :refer [formatter unparse]]
            [newsfrt.subs :as subs]
            [clojure.string :as string]
            [goog.string :as gstring]
            ))

;; components
;; main-panel
;;
;; -div.wrapper
;;
;; --head-panel
;; ---titleslug
;; ---icon
;; ---itemcount
;; ---time-buttons
;; ---custom-query
;;
;; --nav.main.nav
;; ---recent-button
;; ---category-button *
;; ----topic-buttons
;;
;; --content.content
;; ---article*
;; ----art-header
;; ----art-content
;;
;; --aside.side
;; ---author panel
;; --div.ad
;; --footer.main-footer
;;

;; header item
(defn itemcount
  "displays count of topic items in database"
  []
  [:span (str "  Items in database:  " @(rf/subscribe [:item-count]))])

(declare urlize)

(defn make-article
  [{:keys [source created_at author text]}]
  [:article.article
   [:p.art-header (string/join " " [author created_at source])]
   (urlize text)])

(defn recent-button
  []
  [:button.recent-btn {:id "recent"
                       :on-click #(rf/dispatch [:get-recent])}
   "Latest!"])

(defn topic-button
  [[topic desc]]
  [:button.topic-btn {:id topic
                      :on-click #(rf/dispatch [:topic-req topic])}
   desc])

(defn category-button
  [category]
  (let [topic-descs @(rf/subscribe [:topic-descs-by-category category])]
    (into [:div [:button.cat-btn {:id category
                                  :on-click #(rf/dispatch [:category-req
                                                           category])}
                 (name category)]]
        (mapv #(topic-button %1) topic-descs))))

(defn category-buttons []
  (let [categories @(rf/subscribe [:categories])]
    (into [[:div (recent-button)]]
          (mapv category-button categories))))

;; time buttons

(defn time-button [button-id]
  (let [active? (= button-id @(rf/subscribe [:time-button-active-id]))
        cls (if active? "time-btn time-btn-active" "time-btn")]
    [:button {:id button-id
              :class cls} @(rf/subscribe [:button-id-to-text
                                          button-id])]))

(defn time-buttons []
  (let [button-ids @(rf/subscribe [:get-time-button-ids])]
    (into [:div.button-bar
           {:on-click #(rf/dispatch [:set-active-time-button
                                     (keyword
                                      (-> % .-target .-id))])}]
          (mapv time-button button-ids) )))

(defn cal [id]
  (let [label (if (= id :start) "Start Date" "End Date")]
    [re-com/v-box
     :children [[re-com/label :label label]
                [re-com/datepicker :on-change #(rf/dispatch
                   [:set-custom-date id %])
                 :model @(rf/subscribe [:get-custom-date id])
                 :attr {:id id}
                 :show-today? true]]]))

(defn custom-calendar []
  #_(rf/dispatch [:set-custom-date :start (now)])
  #_(rf/dispatch [:set-custom-date :end (now)])
  [re-com/modal-panel
   :backdrop-on-click #(rf/dispatch [:toggle-show-custom-time-panel])
   :wrap-nicely? true
   ;; :child [:span "message"]
   :child [re-com/h-box :gap "20px"
              :children [(cal :start) (cal :end)]]])

;; custom query

(defn verify-custom-query []
  (let [text  @(rf/subscribe [:get-custom-query])]
    (if (re-find #"[\*\.,;\-\"]" text)
      (rf/dispatch [:set-custom-query-status :error])
      (rf/dispatch [:set-custom-query-status :success]))))

(defn on-custom-query-change [text]
  (rf/dispatch-sync [:set-custom-query  text])
  (verify-custom-query))

(defn custom-query []
  [re-com/h-box :class "custom-query"
   :gap "5px"
   :children [
              [:span "Custom Query: "]
              [re-com/info-button :info "Type custom search terms separated by spaces"
               :position :right-center]
              [re-com/input-text
               :model @(rf/subscribe [:get-custom-query])
               :placeholder "Type custom query text here"
               :on-change #(on-custom-query-change %1)
               :change-on-blur? false
               :status @(rf/subscribe [:get-custom-query-status])
               :status-icon? true
               :status-tooltip "Characters * - , ; . \" not allowed"
               :attr {:on-key-press #(when (= (.-key %1) "Enter")
                                       #_(println "Enter")
                                       (rf/dispatch [:custom-query-req
                                                     @(rf/subscribe
                                                      [:get-custom-query])])) }
               ]
              ]])

(defn alert-box []
  (when-let [msg @(rf/subscribe [:alert?])]
    (js/setTimeout #(rf/dispatch [:alert nil]) 5000)
    (re-com/alert-box :id "alert-box"
                      :heading (str "Error: " msg)
                      :alert-type :warning
                      :class "alert-box"
                      :closeable? true
                      :on-close (fn [id](rf/dispatch [:alert nil])))
    ))

(defn help-text []
  (re-com/v-box :children [[:p "After selecting time, you may either:"]
                           [:p "Select categories or topics from left colum"]
                           [:p "Enter a custom query"]
                           [:p "Default shows last 3 hrs of news, all cat"]]))
(defn head-panel []
  [:header.main-head [re-com/h-box :gap "5px"
                      :children [[re-com/label :label "Noozewire Latest News"]
                                 [re-com/info-button :info (help-text)
                                  :position :right-center]
                                 (itemcount)]]
   (time-buttons)
   (custom-query)])

(defn throbber [color]
  [re-com/throbber :color color :size :regular])

(defn fill-content [what]
  (into [:content.content {:id "content1"}] what ))

(defn content []
  (let [abox (alert-box)
        cal @(rf/subscribe [:show-custom-time-panel?])
        thrbr @(rf/subscribe [:cats-loading?])
        recent-loading? @(rf/subscribe [:recent-loading?])]
    (cond
      cal (custom-calendar)
      abox (fill-content [abox])
      thrbr (fill-content [(throbber "yellow")])
      recent-loading? (fill-content [(throbber "red")])
      :else (fill-content (mapv make-article @(rf/subscribe
                                                    [:filtered-statuses]))))))
(defn chkbox [author]
  (re-com/checkbox :label author
                   :model @(rf/subscribe [:get-author-display-state author])
                   :on-change #(rf/dispatch
                     [:toggle-author-display-state author %])))

(defn author-panel []
  (let [authors @(rf/subscribe [:get-authors])]
    (re-com/v-box :children (into [[re-com/checkbox :label "All/None"
                                    :model @(rf/subscribe [:display-all-authors?])
                                    :on-change #(rf/dispatch
                                         [:set-reset-author-display-states %])]
                                   [re-com/line]]
                                  (mapv chkbox authors))))
  )

(defn main-panel []
  [:div.wrapper
   (head-panel)
   (into [:nav.main-nav] (category-buttons))
   (content)
   [:aside.side (author-panel)]
   [:div.ad "ad-text"]
   [:footer.main-footer "News brought to you by Noozewire"]])


;; see https://github.com/reagent-project/reagent
(def setup-main-panel
  (with-meta main-panel
    {:component-will-mount (fn [] (do (.log js/console "main will mount")
                                     (rf/dispatch-sync [:initialize-content])))}))
;; functions below are used in building articles
;; need to turn urls into links and eliminate from text

(defn link-url
  [url]
  [:a {:href url :target "_blank"} " ...more \u21aa"])

(def re-url #"https?://\S+")

(defn extract-urls
  [text]
  (re-seq re-url text))

(defn suppress-urls
  [text]
  (string/replace text re-url ""))

(defn urlize
  [text]
  (let [urls (extract-urls text)
        modtext (gstring/unescapeEntities (suppress-urls text))]
    (into [:p.art-content modtext] (mapv link-url urls))))

;; --- end of urlize-related funcs ----------
