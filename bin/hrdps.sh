d=2015-01-01
while [ "$d" != 2015-02-20 ]; do
  echo $d
  d=$(date -I -d "$d + 1 day")

  # mac option for d decl (the +1d is equivalent to + 1 day)
  # d=$(date -j -v +1d -f "%Y-%m-%d" $d +%Y-%m-%d)
done
