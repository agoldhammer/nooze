(ns newsfrt.runner
    (:require [doo.runner :refer-macros [doo-tests]]
              [newsfrt.core-test]))

(doo-tests 'newsfrt.core-test)
