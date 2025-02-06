#include <bits/stdc++.h>
#define all(x) begin(x), end(x)
#define rall(x) rbegin(x), rend(x)
using namespace std;
using ll = long long;

template<class T> using pq_min = priority_queue<T,vector<T>,greater<T>>;
template<class T> using pq_max = priority_queue<T,vector<T>,less<T>>;

struct Card {
  int number;
  int color;
  int time;
  set<int> incorrect;
};

bool operator<(const Card& a, const Card& b) {
  if (a.number == b.number) return a.color < b.color;
  return a.number < b.number;
}

bool operator>(const Card& a, const Card& b) {
  if (a.number == b.number) return a.color > b.color;
  return a.number > b.number;
}

bool operator==(const Card& a, const Card& b) {
  return a.number == b.number && a.color == b.color;
}

ostream& operator<<(ostream& os, const Card& a) {
  os << "{" << a.number << " " << a.color << " " << a.time << " {";
  for (auto x:a.incorrect) os << x << " ";
  os << "}}";
  return os;
}

void solve() {
  int n;
  cin >> n;
  vector<Card> a(n);
  vector<bool> revealed(n, false);
  for (int i = 0; i < n; ++i) {
    int x, c, t, m;
    cin >> x >> c >> t >> m;
    set<int> incorrect;
    for (int j = 0; j < m; ++j) {
      int val;
      cin >> val;
      incorrect.insert(val);
    }
    a[i] = {x, c, t, incorrect};
    if (x != -1) revealed[t] = true;
  }

  int m;
  cin >> m;
  set<Card> b;
  for (int i = 0; i < m; ++i) {
    int x, c;
    cin >> x >> c;
    b.insert({x, c, -1, set<int>()});
  }

  vector<vector<int>> counts(n, vector<int> (12,0));

  auto dfs = [&] (int pos, auto&& dfs) {
    if (pos == -1) {
      //for (auto i : a) {
      //  cout << i << " ";
      //}
      //cout << endl;
      for (int i = 0; i < n; ++i) {
        counts[a[i].time][a[i].number]++;
      }
      return 1;
    }
    if (a[pos].number == -1) {
      int sum = 0;
      int color = a[pos].color;
      for (int i = 0; i < 12; ++i) {
        Card card = {i, color, -1, set<int>()};
        if (b.find(card) != b.end()) {
          continue; // Card is already in opponent's hand
        }
        if (find(a.begin(), a.end(), card) != a.end()) {
          continue; // Card is already in your hand
        }
        if (0 < pos && a[pos-1].number != -1 && a[pos-1] > card) {
          continue; // Check behind
        }
        if (pos < n-1 && a[pos+1].number != -1 && card > a[pos+1]) {
          continue; // Check in front
        }
        if (a[pos].incorrect.find(i) != a[pos].incorrect.end()) {
          continue; // This was a previously incorrect guess
        }
        a[pos].number = i;
        sum += dfs(pos - 1, dfs);
        a[pos].number = -1;
      }
      return sum;
    }
    return dfs(pos-1, dfs);
  };

  int tot = dfs(n-1, dfs);

  double best = 0;
  int bestPos = 0;
  int bestGuess = 0;
  cout << tot << endl;
  for (int i = 0; i < n; ++i) {
    cout << "card " << (i < 10 ? " " : "") << i << ": ";
    for (int j = 0; j < 12; ++j) {
      double res = double(counts[i][j]) / double(tot);
      cout << fixed << setprecision(6) << res << " ";
      if (!revealed[i] && best < res) {
        best = res;
        bestPos = i;
        bestGuess = j;
      }
    }
    cout << endl;
  }

  cout << "You should guess " << bestGuess << " for card " << bestPos << " for a probability " << best << endl;

}

int main() {
  ios_base::sync_with_stdio(false);
  cin.tie(0);
  int t = 1;
  // cin >> t;
  while (t--) solve();
  #ifdef LOCAL_TIME
    cerr << "Time elapsed: " << 1.0 * clock() / CLOCKS_PER_SEC << "s\n";
  #endif
}
